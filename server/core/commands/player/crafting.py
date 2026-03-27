"""
Crafting / Artisan Guild commands.

Current live scope:
  ARTISAN shell commands
  Starter fletching vertical slice for hunting arrows
"""

from __future__ import annotations

import random
import re
from datetime import datetime

from server.core.protocol.colors import colorize, TextPresets, item_name as fmt_item_name, roundtime_msg
from server.core.commands.player.inventory import _ensure_hands, _find_in_hands, auto_stow_item


def _cfg(server):
    lua = getattr(server, "lua", None)
    return getattr(lua, "get_crafting", lambda: None)() if lua else None


def _norm(text):
    return (text or "").strip().lower().replace(" ", "_").replace("-", "_")


def _recipe(cfg, key="fletching_hunting_arrow"):
    return ((cfg or {}).get("recipes") or {}).get(key) or {}


def _station(cfg, key):
    return ((cfg or {}).get("stations") or {}).get(key) or {}


def _strip_article(name):
    text = str(name or "").strip()
    parts = text.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() in ("a", "an", "the", "some"):
        return parts[1]
    return text


def _rank_label(cfg, ranks):
    for band in cfg.get("rank_bands", []):
        if int(band.get("min", 0)) <= ranks <= int(band.get("max", 0)):
            return str(band.get("label") or "Novice")
    return "Novice"


def _item_key(recipe, key):
    return str((recipe.get("item_keys") or {}).get(key) or "").strip()


def _item_matches_short(item, short_name):
    return short_name and str(item.get("short_name") or "").strip().lower() == short_name.lower()


def _weaponish(item, *nouns):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    weapon_type = str(item.get("weapon_type") or "").strip().lower()
    wanted = {str(n).strip().lower() for n in nouns}
    return noun in wanted or any(token in short_name for token in wanted) or weapon_type in wanted


def _is_handaxe(item):
    return _weaponish(item, "handaxe", "hatchet")


def _is_dagger(item):
    return _weaponish(item, "dagger", "knife")


def _is_bow(item):
    return _weaponish(item, "bow") or str(item.get("weapon_type") or "").strip().lower() == "ranged"


def _is_wood(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "wood_source")) or noun == "branch" or "branch" in short_name


def _is_shaft(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "shaft")) or (
        noun == "shaft" and str(item.get("crafting_recipe") or "") == str(recipe.get("key") or "")
    )


def _is_glue(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "glue")) or noun == "glue" or "glue" in short_name


def _is_fletching(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "fletchings")) or noun in ("fletching", "fletchings", "feather", "feathers") or "fletch" in short_name


def _is_upper(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "upper")) or noun == "upper" or "upper" in short_name


def _is_sole(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "sole")) or noun == "sole" or "sole" in short_name


def _is_chalk(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "chalk")) or noun == "chalk" or "chalk" in short_name


def _is_cord(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    short_name = str(item.get("short_name") or "").strip().lower()
    return _item_matches_short(item, _item_key(recipe, "cord")) or noun == "cord" or "cord" in short_name


def _is_slippers(item, recipe):
    noun = str(item.get("noun") or "").strip().lower()
    return _item_matches_short(item, str(recipe.get("output_item_short_name") or _item_key(recipe, "output"))) or (
        noun in ("slippers", "slipper") and str(item.get("crafting_recipe") or "") == str(recipe.get("key") or "")
    )


def _stage(item):
    return str(item.get("crafting_stage") or "").strip().lower()


def _stage_label(recipe, stage_key):
    for row in recipe.get("stages") or []:
        if str(row.get("key") or "") == stage_key:
            return str(row.get("label") or stage_key)
    return stage_key.replace("_", " ")


def _stage_index(recipe, stage_key):
    for idx, row in enumerate(recipe.get("stages") or [], start=1):
        if str(row.get("key") or "") == stage_key:
            return idx
    return 0


def _room_allows(session, cfg, recipe):
    room = getattr(session, "current_room", None)
    if not room:
        return False
    tags = {str(t).strip().lower() for t in getattr(room, "tags", []) or [] if str(t).strip()}
    needed = {str(t).strip().lower() for t in (_station(cfg, recipe.get("station") or "").get("room_tags") or []) if str(t).strip()}
    return not needed or bool(tags & needed)


def _set_name(item, name):
    item["name"] = name
    item["short_name"] = _strip_article(name)


def _save_shaft(server, item, recipe, stage_key, name):
    _set_name(item, name)
    item["crafting_recipe"] = str(recipe.get("key") or "")
    item["crafting_stage"] = stage_key
    if item.get("inv_id") and getattr(server, "db", None):
        server.db.save_item_extra_data(item["inv_id"], {
            "crafting_recipe": str(recipe.get("key") or ""),
            "crafting_stage": stage_key,
            "custom_name": name,
        })


def _to_runtime(template):
    item = dict(template or {})
    item["item_id"] = template.get("id")
    item.pop("id", None)
    item.pop("created_at", None)
    return item


def _consume_held(session, server, item):
    inv_id = item.get("inv_id")
    if getattr(session, "right_hand", None) is item:
        session.right_hand = None
    elif getattr(session, "left_hand", None) is item:
        session.left_hand = None
    if inv_id and getattr(server, "db", None):
        server.db.remove_item_from_inventory(inv_id)
    session.inventory = [row for row in getattr(session, "inventory", []) if row.get("inv_id") != inv_id]


def _progress(server, char_id, skill):
    return (server.db.get_character_artisan_skills(char_id) or {}).get(skill) or {}


def _quality(ranks):
    if ranks >= 75:
        return "excellent"
    if ranks >= 40:
        return "sound"
    if ranks >= 15:
        return "serviceable"
    return "crude"


def _upsert_project(server, session, recipe, shaft, stage_key, quality_tier):
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        return
    server.db.upsert_active_artisan_project(
        session.character_id,
        "fletching",
        str(recipe.get("key") or ""),
        station_key=str(recipe.get("station") or ""),
        stage_index=_stage_index(recipe, stage_key),
        quality_tier=quality_tier,
        recipe_snapshot=recipe,
        progress_data={"shaft_inv_id": shaft.get("inv_id"), "stage": stage_key},
    )


async def _award_completion(session, server, recipe, quality_tier):
    row = _progress(server, session.character_id, "fletching")
    ranks = int(row.get("ranks", 0) or 0)
    completed = int(row.get("projects_completed", 0) or 0) + 1
    step = max(1, int(recipe.get("rank_projects") or 1))
    gained = completed % step == 0
    if gained:
        ranks += 1
    server.db.save_character_artisan_skill(
        session.character_id, "fletching", ranks,
        projects_completed=completed, last_worked_at=datetime.utcnow()
    )
    server.db.complete_character_artisan_project(
        session.character_id, "fletching",
        progress_data={"completed_projects": completed, "quality_tier": quality_tier},
        quality_tier=quality_tier,
    )
    if gained:
        await session.send_line(colorize(f"Your fletching improves to {ranks} ranks.", TextPresets.SUCCESS))


async def _award_cobbling_completion(session, server, recipe, quality_tier):
    row = _progress(server, session.character_id, "cobbling")
    ranks = int(row.get("ranks", 0) or 0)
    completed = int(row.get("projects_completed", 0) or 0) + 1
    step = max(1, int(recipe.get("rank_projects") or 1))
    gained = completed % step == 0
    if gained:
        ranks += 1
    server.db.save_character_artisan_skill(
        session.character_id, "cobbling", ranks,
        projects_completed=completed, last_worked_at=datetime.utcnow()
    )
    server.db.complete_character_artisan_project(
        session.character_id, "cobbling",
        progress_data={"completed_projects": completed, "quality_tier": quality_tier},
        quality_tier=quality_tier,
    )
    if gained:
        await session.send_line(colorize(f"Your cobbling improves to {ranks} ranks.", TextPresets.SUCCESS))


async def _rt(session, seconds):
    if hasattr(session, "set_roundtime"):
        session.set_roundtime(seconds)
        await session.send_line(roundtime_msg(seconds))


async def _artisan_help(session, cfg):
    await session.send_line(colorize("Artisan skill commands:", TextPresets.SYSTEM))
    await session.send_line("  ARTISAN HELP                    - Displays this message.")
    await session.send_line("  ARTISAN SKILLS                  - Displays your ranks in various skills.")
    await session.send_line("  ARTISAN RANKS                   - Displays the text to rank information.")
    await session.send_line("  ARTISAN UNLEARN CHECK           - Checks your unlearning preference.")
    await session.send_line("  ARTISAN UNLEARN HELP            - Explains artisan unlearning.")
    await session.send_line("  ARTISAN UNLEARN SET <skill>     - Sets your unlearning preference.")
    await session.send_line("  Skills: " + ", ".join(str((row or {}).get("command_token") or "").strip() for row in (cfg.get("skills") or {}).values() if row))


async def _artisan_skills(session, server, cfg):
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        await session.send_line("The Artisan Guild ledgers are unavailable right now.")
        return
    rows = server.db.get_character_artisan_skills(session.character_id) or {}
    total = 0
    for key in cfg.get("skill_order") or []:
        ranks = int((rows.get(key) or {}).get("ranks", 0) or 0)
        total += ranks
        label = str((((cfg.get("skills") or {}).get(key) or {}).get("label")) or key)
        await session.send_line(f"In the skill of {label.lower()}, you are a {_rank_label(cfg, ranks).lower()} laborer with {ranks} ranks.")
    await session.send_line(f"Total artisan ranks: {total} / {int(cfg.get('total_rank_limit', 1200) or 1200)}")


async def _artisan_ranks(session, cfg):
    await session.send_line(colorize("Artisan rank titles:", TextPresets.SYSTEM))
    for band in cfg.get("rank_bands", []):
        await session.send_line(f"  {band.get('label')}: {band.get('min')} - {band.get('max')}")


async def _artisan_unlearn(session, server, cfg, raw):
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        await session.send_line("The Artisan Guild ledgers are unavailable right now.")
        return
    parts = raw.split()
    if not parts:
        await session.send_line("Usage: ARTISAN UNLEARN CHECK, HELP, or SET <skill>.")
        return
    sub = parts[0].lower()
    if sub == "check":
        settings = server.db.get_character_artisan_settings(session.character_id) or {}
        pref = str(settings.get("unlearn_preference_key") or "none").strip() or "none"
        await session.send_line(f"Current unlearning preference: {pref}")
        return
    if sub == "help":
        await session.send_line("Use ARTISAN UNLEARN SET <skill> to choose which artisan skill fades first if you exceed the shared artisan rank limit.")
        return
    if sub == "set":
        token = _norm(" ".join(parts[1:]))
        if token == "none":
            ok = server.db.set_character_artisan_unlearn_preference(session.character_id, None)
            await session.send_line("You consciously choose to learn no more." if ok else "Your artisan unlearning preference could not be updated.")
            return
        mapping = _skill_map(cfg)
        row = mapping.get(token)
        if not row:
            await session.send_line("That is not a valid artisan skill.")
            return
        ok = server.db.set_character_artisan_unlearn_preference(session.character_id, str(row.get("key") or ""))
        await session.send_line(f"Setting your unlearning preference to {str(row.get('command_token') or row.get('key')).lower()}." if ok else "Your artisan unlearning preference could not be updated.")
        return
    await session.send_line("Usage: ARTISAN UNLEARN CHECK, HELP, or SET <skill>.")


def _skill_map(cfg):
    out = {}
    for key, row in (cfg.get("skills") or {}).items():
        out[_norm(key)] = row
        out[_norm(row.get("label") or key)] = row
        out[_norm(row.get("command_token") or key)] = row
    return out


async def cmd_artisan(session, cmd, args, server):
    cfg = _cfg(server)
    if not cfg:
        await session.send_line("The Artisan Guild system is not available right now.")
        return
    raw = (args or "").strip()
    if not raw or raw.lower() == "help":
        await _artisan_help(session, cfg)
        return
    head, _, tail = raw.partition(" ")
    head = head.lower()
    if head == "skills":
        await _artisan_skills(session, server, cfg)
        return
    if head == "ranks":
        await _artisan_ranks(session, cfg)
        return
    if head == "unlearn":
        await _artisan_unlearn(session, server, cfg, tail.strip())
        return
    await session.send_line("Usage: ARTISAN HELP, ARTISAN SKILLS, ARTISAN RANKS, or ARTISAN UNLEARN ...")


async def _fletching_help(session, recipe):
    await session.send_line(colorize("Fletching commands:", TextPresets.SYSTEM))
    await session.send_line("  FLETCHING HELP       - Displays this message.")
    await session.send_line("  FLETCHING MATERIALS  - Displays the starter arrow requirements.")
    await session.send_line("  FLETCHING CHECK      - Displays your current arrow project status.")
    for row in recipe.get("stages") or []:
        label = str(row.get("label") or "").strip()
        command = str(row.get("command") or "").strip()
        if label and command:
            await session.send_line(f"  {label}: {command}")


async def _fletching_materials(session, recipe):
    await session.send_line(colorize("Starter hunting-arrow requirements:", TextPresets.SYSTEM))
    for tool in recipe.get("tools") or []:
        await session.send_line(f"  Tool: {tool.get('label')}")
    for mat in recipe.get("materials") or []:
        count = int(mat.get("count") or 0)
        label = str(mat.get("label") or mat.get("key") or "").strip()
        consume = "consumed" if mat.get("consume", True) else "reused"
        await session.send_line(f"  {count}x {label} ({consume})")


async def _fletching_check(session, server, cfg, recipe):
    row = _progress(server, session.character_id, "fletching") if getattr(session, "character_id", None) else {}
    ranks = int(row.get("ranks", 0) or 0)
    await session.send_line(colorize("Fletching status:", TextPresets.SYSTEM))
    await session.send_line(f"  Ranks: {ranks} ({_rank_label(cfg, ranks)})")
    await session.send_line(f"  Completed projects: {int(row.get('projects_completed', 0) or 0)}")
    for hand_attr, hand_label in (("right_hand", "right hand"), ("left_hand", "left hand")):
        item = getattr(session, hand_attr, None)
        if item and _is_shaft(item, recipe):
            await session.send_line(f"  In your {hand_label}: {_stage_label(recipe, _stage(item) or 'rough')}")
    active = server.db.get_character_active_artisan_project(session.character_id, "fletching") if getattr(server, "db", None) and getattr(session, "character_id", None) else None
    if active:
        progress = active.get("progress_data") or {}
        await session.send_line(f"  Active project stage: {_stage_label(recipe, str(progress.get('stage') or 'unknown'))}")


async def _rough_shafts(session, server, cfg, recipe, wood_name, tool_name):
    _ensure_hands(session)
    if not _room_allows(session, cfg, recipe):
        await session.send_line("You need to be in a proper fletching shop or workroom to cut fresh shafts.")
        return
    wood, wood_hand = _find_in_hands(session, wood_name)
    tool, tool_hand = _find_in_hands(session, tool_name)
    if not wood or not tool:
        await session.send_line("You need to be holding both the wood and the handaxe first.")
        return
    if wood_hand == tool_hand:
        await session.send_line("You need the wood and the handaxe in different hands.")
        return
    if not _is_wood(wood, recipe):
        await session.send_line("That is not a suitable wood source for starter arrow shafts.")
        return
    if not _is_handaxe(tool):
        await session.send_line("You need a handaxe or hatchet for that step.")
        return
    template = server.db.get_item_template_by_short_name(_item_key(recipe, "shaft"))
    if not template:
        await session.send_line("The fletching pattern for arrow shafts is unavailable right now.")
        return
    _consume_held(session, server, wood)
    created = 0
    for _ in range(random.randint(int(recipe.get("rough_yield_min") or 1), int(recipe.get("rough_yield_max") or recipe.get("rough_yield_min") or 1))):
        shaft = _to_runtime(template)
        _set_name(shaft, "a rough arrow shaft")
        shaft["crafting_recipe"] = str(recipe.get("key") or "")
        shaft["crafting_stage"] = "rough"
        success, _, _ = auto_stow_item(session, server, shaft)
        if not success:
            break
        _save_shaft(server, shaft, recipe, "rough", "a rough arrow shaft")
        created += 1
    if created <= 0:
        await session.send_line("You do not have room to keep the shafts you would cut.")
        return
    await session.send_line(f"You cut {created} rough arrow shaft{'s' if created != 1 else ''} from {fmt_item_name(wood.get('short_name') or 'the wood')}.")
    if getattr(server, "world", None) and getattr(session, "current_room", None):
        await server.world.broadcast_to_room(session.current_room.id, f"{session.character_name} trims several rough shafts from a piece of wood.", exclude=session)
    await _rt(session, 3)


async def _work_shaft(session, server, recipe, shaft_name, tool_name):
    _ensure_hands(session)
    shaft, shaft_hand = _find_in_hands(session, shaft_name)
    tool, tool_hand = _find_in_hands(session, tool_name)
    if not shaft or not tool:
        await session.send_line("You need to be holding both the shaft and the dagger first.")
        return
    if shaft_hand == tool_hand:
        await session.send_line("You need the shaft and the dagger in different hands.")
        return
    if not _is_shaft(shaft, recipe):
        await session.send_line("That is not a fletching shaft you can work right now.")
        return
    if not _is_dagger(tool):
        await session.send_line("You need a dagger or knife for that step.")
        return
    stage = _stage(shaft) or "rough"
    quality_tier = _quality(int((_progress(server, session.character_id, "fletching") or {}).get("ranks", 0) or 0))
    if stage == "rough":
        _save_shaft(server, shaft, recipe, "pared", "an arrow shaft")
        _upsert_project(server, session, recipe, shaft, "pared", quality_tier)
        await session.send_line("You carefully pare the rough shaft down until it lies straighter in your grip.")
        await _rt(session, 3)
        return
    if stage == "measured":
        _save_shaft(server, shaft, recipe, "trimmed", "a trimmed arrow shaft")
        _upsert_project(server, session, recipe, shaft, "trimmed", quality_tier)
        await session.send_line("You cut the measured shaft cleanly to the proper length.")
        await _rt(session, 3)
        return
    if stage == "fletched":
        template = server.db.get_item_template_by_short_name(str(recipe.get("output_item_short_name") or _item_key(recipe, "output")))
        if not template:
            await session.send_line("The finished arrow pattern is unavailable right now.")
            return
        _consume_held(session, server, shaft)
        arrow = _to_runtime(template)
        success, location, _ = auto_stow_item(session, server, arrow)
        if not success:
            await session.send_line("You lack the room to keep the finished arrow.")
            return
        await session.send_line(f"You whittle the tip to a clean point, completing {fmt_item_name(arrow.get('short_name') or 'an arrow')} and placing it in your {location}.")
        await _award_completion(session, server, recipe, quality_tier)
        if getattr(server, "world", None) and getattr(session, "current_room", None):
            await server.world.broadcast_to_room(session.current_room.id, f"{session.character_name} finishes shaping an arrow point with practiced care.", exclude=session)
        await _rt(session, 3)
        return
    if stage == "pared":
        await session.send_line("The shaft is pared, but it still needs nocks cut into it.")
        return
    if stage == "nocked":
        await session.send_line("The shaft is ready to be measured against a bow.")
        return
    if stage == "trimmed":
        await session.send_line("The shaft has been cut to length.  It needs glue next.")
        return
    if stage == "glued":
        await session.send_line("The glue is on the shaft already.  Attach the fletchings next.")
        return
    await session.send_line("You are not ready to cut that shaft any further.")


async def _cut_nocks(session, server, recipe, shaft_name, tool_name):
    shaft, shaft_hand = _find_in_hands(session, shaft_name)
    tool, tool_hand = _find_in_hands(session, tool_name)
    if not shaft or not tool or shaft_hand == tool_hand:
        await session.send_line("You need the shaft and the dagger in different hands.")
        return
    if not _is_shaft(shaft, recipe) or not _is_dagger(tool):
        await session.send_line("You need a shaft and a dagger for that step.")
        return
    if _stage(shaft) != "pared":
        await session.send_line("You need to pare the shaft before cutting nocks into it.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "fletching") or {}).get("ranks", 0) or 0))
    _save_shaft(server, shaft, recipe, "nocked", "a nocked arrow shaft")
    _upsert_project(server, session, recipe, shaft, "nocked", quality_tier)
    await session.send_line("You cut careful nocks into the end of the shaft for the bowstring.")
    await _rt(session, 3)


async def _measure_shaft(session, server, recipe, shaft_name, tool_name):
    shaft, shaft_hand = _find_in_hands(session, shaft_name)
    tool, tool_hand = _find_in_hands(session, tool_name)
    if not shaft or not tool or shaft_hand == tool_hand:
        await session.send_line("You need the shaft and the bow in different hands.")
        return
    if not _is_shaft(shaft, recipe) or not _is_bow(tool):
        await session.send_line("You need a shaft and a bow for that step.")
        return
    if _stage(shaft) != "nocked":
        await session.send_line("The shaft needs nocks before you can measure it properly.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "fletching") or {}).get("ranks", 0) or 0))
    _save_shaft(server, shaft, recipe, "measured", "a measured arrow shaft")
    _upsert_project(server, session, recipe, shaft, "measured", quality_tier)
    await session.send_line("You sight along the bow and mark the shaft for a proper hunting-arrow length.")
    await _rt(session, 3)


async def _glue_shaft(session, server, recipe, glue_name, shaft_name):
    glue, glue_hand = _find_in_hands(session, glue_name)
    shaft, shaft_hand = _find_in_hands(session, shaft_name)
    if not glue or not shaft or glue_hand == shaft_hand:
        await session.send_line("You need the glue and the shaft in different hands.")
        return
    if not _is_glue(glue, recipe) or not _is_shaft(shaft, recipe):
        await session.send_line("You need fletching glue and a proper shaft for that step.")
        return
    if _stage(shaft) != "trimmed":
        await session.send_line("The shaft needs to be cut to length before you apply glue.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "fletching") or {}).get("ranks", 0) or 0))
    _save_shaft(server, shaft, recipe, "glued", "a glued arrow shaft")
    _upsert_project(server, session, recipe, shaft, "glued", quality_tier)
    await session.send_line("You apply a careful line of fletching glue along the rear of the shaft.")
    await _rt(session, 2)


async def _fletch_shaft(session, server, recipe, fletching_name, shaft_name):
    fletching, fletching_hand = _find_in_hands(session, fletching_name)
    shaft, shaft_hand = _find_in_hands(session, shaft_name)
    if not fletching or not shaft or fletching_hand == shaft_hand:
        await session.send_line("You need the fletchings and the shaft in different hands.")
        return
    if not _is_fletching(fletching, recipe) or not _is_shaft(shaft, recipe):
        await session.send_line("You need proper fletchings and a shaft for that step.")
        return
    if _stage(shaft) != "glued":
        await session.send_line("You need to glue the shaft before attaching fletchings.")
        return
    _consume_held(session, server, fletching)
    quality_tier = _quality(int((_progress(server, session.character_id, "fletching") or {}).get("ranks", 0) or 0))
    _save_shaft(server, shaft, recipe, "fletched", "a fletched arrow shaft")
    _upsert_project(server, session, recipe, shaft, "fletched", quality_tier)
    await session.send_line("You press the goose fletchings neatly into the glue and align them by eye.")
    await _rt(session, 2)


def _save_slippers(server, item, recipe, stage_key, name):
    _set_name(item, name)
    item["crafting_recipe"] = str(recipe.get("key") or "")
    item["crafting_stage"] = stage_key
    if item.get("inv_id") and getattr(server, "db", None):
        server.db.save_item_extra_data(item["inv_id"], {
            "crafting_recipe": str(recipe.get("key") or ""),
            "crafting_stage": stage_key,
            "custom_name": name,
        })


def _upsert_cobbling_project(server, session, recipe, slippers, stage_key, quality_tier):
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        return
    server.db.upsert_active_artisan_project(
        session.character_id,
        "cobbling",
        str(recipe.get("key") or ""),
        station_key=str(recipe.get("station") or ""),
        stage_index=_stage_index(recipe, stage_key),
        quality_tier=quality_tier,
        recipe_snapshot=recipe,
        progress_data={"slippers_inv_id": slippers.get("inv_id"), "stage": stage_key},
    )


async def _cobbling_help(session, recipe):
    await session.send_line(colorize("Cobbling commands:", TextPresets.SYSTEM))
    await session.send_line("  COBBLING HELP             - Displays this message.")
    await session.send_line("  COBBLING MATERIALS        - Displays the starter slipper requirements.")
    await session.send_line("  COBBLING CHECK            - Displays your current slipper project status.")
    await session.send_line("  COBBLING START SLIPPERS   - Joins a leather upper and sole.")
    await session.send_line("  COBBLING CHALK MY SLIPPERS")
    await session.send_line("  COBBLING CUT MY SLIPPERS")
    await session.send_line("  COBBLING FIT MY SLIPPERS")
    await session.send_line("  COBBLING FINISH MY SLIPPERS")
    for row in recipe.get("stages") or []:
        label = str(row.get("label") or "").strip()
        command = str(row.get("command") or "").strip()
        if label and command:
            await session.send_line(f"  {label}: {command}")


async def _cobbling_materials(session, recipe):
    await session.send_line(colorize("Starter leather-slipper requirements:", TextPresets.SYSTEM))
    for tool in recipe.get("tools") or []:
        await session.send_line(f"  Tool: {tool.get('label')}")
    for mat in recipe.get("materials") or []:
        count = int(mat.get("count") or 0)
        label = str(mat.get("label") or mat.get("key") or "").strip()
        consume = "consumed" if mat.get("consume", True) else "reused"
        await session.send_line(f"  {count}x {label} ({consume})")


async def _cobbling_check(session, server, cfg, recipe):
    row = _progress(server, session.character_id, "cobbling") if getattr(session, "character_id", None) else {}
    ranks = int(row.get("ranks", 0) or 0)
    await session.send_line(colorize("Cobbling status:", TextPresets.SYSTEM))
    await session.send_line(f"  Ranks: {ranks} ({_rank_label(cfg, ranks)})")
    await session.send_line(f"  Completed projects: {int(row.get('projects_completed', 0) or 0)}")
    for hand_attr, hand_label in (("right_hand", "right hand"), ("left_hand", "left hand")):
        item = getattr(session, hand_attr, None)
        if item and _is_slippers(item, recipe):
            await session.send_line(f"  In your {hand_label}: {_stage_label(recipe, _stage(item) or 'started')}")
    active = server.db.get_character_active_artisan_project(session.character_id, "cobbling") if getattr(server, "db", None) and getattr(session, "character_id", None) else None
    if active:
        progress = active.get("progress_data") or {}
        await session.send_line(f"  Active project stage: {_stage_label(recipe, str(progress.get('stage') or 'unknown'))}")


async def _start_slippers(session, server, cfg, recipe):
    _ensure_hands(session)
    if not _room_allows(session, cfg, recipe):
        await session.send_line("You need to be in a proper cobbler's shop or workroom to begin that project.")
        return
    upper = getattr(session, "right_hand", None)
    sole = getattr(session, "left_hand", None)
    swapped = False
    if not (_is_upper(upper, recipe) and _is_sole(sole, recipe)):
        upper = getattr(session, "left_hand", None)
        sole = getattr(session, "right_hand", None)
        swapped = True
    if not (_is_upper(upper, recipe) and _is_sole(sole, recipe)):
        await session.send_line("You need a leather upper in one hand and a leather sole in the other.")
        return
    template = server.db.get_item_template_by_short_name(str(recipe.get("output_item_short_name") or _item_key(recipe, "output")))
    if not template:
        await session.send_line("The slipper pattern is unavailable right now.")
        return
    _consume_held(session, server, upper)
    _consume_held(session, server, sole)
    slippers = _to_runtime(template)
    success, _, _ = auto_stow_item(session, server, slippers)
    if not success:
        await session.send_line("You do not have room to keep the unfinished slippers.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "cobbling") or {}).get("ranks", 0) or 0))
    _save_slippers(server, slippers, recipe, "started", "a pair of unfinished leather slippers")
    _upsert_cobbling_project(server, session, recipe, slippers, "started", quality_tier)
    await session.send_line("You join the upper and sole into a pair of unfinished leather slippers.")
    if getattr(server, "world", None) and getattr(session, "current_room", None):
        await server.world.broadcast_to_room(session.current_room.id, f"{session.character_name} starts a pair of leather slippers on the workbench.", exclude=session)
    await _rt(session, 3)


async def _chalk_slippers(session, server, recipe):
    chalk, chalk_hand = _find_in_hands(session, "chalk")
    slippers, slippers_hand = _find_in_hands(session, "slippers")
    if not chalk or not slippers or chalk_hand == slippers_hand:
        await session.send_line("You need the chalk and the slippers in different hands.")
        return
    if not _is_chalk(chalk, recipe) or not _is_slippers(slippers, recipe):
        await session.send_line("You need tailor's chalk and your unfinished slippers for that step.")
        return
    if _stage(slippers) != "started":
        await session.send_line("The slippers are not ready to be marked with chalk yet.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "cobbling") or {}).get("ranks", 0) or 0))
    _save_slippers(server, slippers, recipe, "chalked", "a pair of chalk-marked leather slippers")
    _upsert_cobbling_project(server, session, recipe, slippers, "chalked", quality_tier)
    await session.send_line("You mark the leather with chalk where the trim needs to be neatened.")
    await _rt(session, 2)


async def _cut_slippers(session, server, recipe):
    tool, tool_hand = _find_in_hands(session, "dagger")
    slippers, slippers_hand = _find_in_hands(session, "slippers")
    if not tool or not slippers or tool_hand == slippers_hand:
        await session.send_line("You need the dagger and the slippers in different hands.")
        return
    if not _is_dagger(tool) or not _is_slippers(slippers, recipe):
        await session.send_line("You need a dagger and your slippers for that step.")
        return
    if _stage(slippers) != "chalked":
        await session.send_line("You need to chalk the slippers before trimming them.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "cobbling") or {}).get("ranks", 0) or 0))
    _save_slippers(server, slippers, recipe, "cut", "a pair of trimmed leather slippers")
    _upsert_cobbling_project(server, session, recipe, slippers, "cut", quality_tier)
    await session.send_line("You trim the leather edges down along the chalked lines.")
    await _rt(session, 3)


async def _fit_slippers(session, server, recipe):
    cord, cord_hand = _find_in_hands(session, "cord")
    slippers, slippers_hand = _find_in_hands(session, "slippers")
    if not cord or not slippers or cord_hand == slippers_hand:
        await session.send_line("You need the measuring cord and the slippers in different hands.")
        return
    if not _is_cord(cord, recipe) or not _is_slippers(slippers, recipe):
        await session.send_line("You need a measuring cord and your slippers for that step.")
        return
    if _stage(slippers) != "cut":
        await session.send_line("You need to trim the slippers before measuring their fit.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "cobbling") or {}).get("ranks", 0) or 0))
    _save_slippers(server, slippers, recipe, "fit", "a fitted pair of leather slippers")
    _upsert_cobbling_project(server, session, recipe, slippers, "fit", quality_tier)
    await session.send_line("You measure the slippers carefully with the cord, setting their final fit.")
    await _rt(session, 2)


async def _finish_slippers(session, server, recipe):
    slippers, _ = _find_in_hands(session, "slippers")
    if not slippers or not _is_slippers(slippers, recipe):
        await session.send_line("You need to be holding the slippers first.")
        return
    if _stage(slippers) != "fit":
        await session.send_line("The slippers still need to be measured before you can finish them.")
        return
    quality_tier = _quality(int((_progress(server, session.character_id, "cobbling") or {}).get("ranks", 0) or 0))
    _save_slippers(server, slippers, recipe, "finished", "some leather slippers")
    await _award_cobbling_completion(session, server, recipe, quality_tier)
    await session.send_line("You smooth the last rough edge and finish a tidy pair of leather slippers.")
    if getattr(server, "world", None) and getattr(session, "current_room", None):
        await server.world.broadcast_to_room(session.current_room.id, f"{session.character_name} finishes a pair of leather slippers.", exclude=session)
    await _rt(session, 3)


async def cmd_fletching(session, cmd, args, server):
    cfg = _cfg(server)
    recipe = _recipe(cfg)
    if not cfg or not recipe:
        await session.send_line("Fletching patterns are unavailable right now.")
        return
    raw = (args or "").strip().lower()
    if not raw or raw == "help":
        await _fletching_help(session, recipe)
        return
    if raw in {"materials", "material", "supplies"}:
        await _fletching_materials(session, recipe)
        return
    if raw in {"check", "status"}:
        await _fletching_check(session, server, cfg, recipe)
        return
    await session.send_line("Usage: FLETCHING HELP, FLETCHING MATERIALS, or FLETCHING CHECK.")


async def cmd_cobbling(session, cmd, args, server):
    cfg = _cfg(server)
    recipe = _recipe(cfg, "cobbling_leather_slippers")
    if not cfg or not recipe:
        await session.send_line("Cobbling patterns are unavailable right now.")
        return
    raw = (args or "").strip().lower()
    if not raw or raw == "help":
        await _cobbling_help(session, recipe)
        return
    if raw in {"materials", "material", "supplies"}:
        await _cobbling_materials(session, recipe)
        return
    if raw in {"check", "status"}:
        await _cobbling_check(session, server, cfg, recipe)
        return
    if raw == "start slippers":
        await _start_slippers(session, server, cfg, recipe)
        return
    if raw in {"chalk my slippers", "chalk slippers"}:
        await _chalk_slippers(session, server, recipe)
        return
    if raw in {"cut my slippers", "cut slippers"}:
        await _cut_slippers(session, server, recipe)
        return
    if raw in {"fit my slippers", "fit slippers"}:
        await _fit_slippers(session, server, recipe)
        return
    if raw in {"finish my slippers", "finish slippers"}:
        await _finish_slippers(session, server, recipe)
        return
    await session.send_line("Usage: COBBLING HELP, MATERIALS, CHECK, START SLIPPERS, CHALK MY SLIPPERS, CUT MY SLIPPERS, FIT MY SLIPPERS, or FINISH MY SLIPPERS.")


async def cmd_cut(session, cmd, args, server):
    cfg = _cfg(server)
    recipe = _recipe(cfg)
    if not cfg or not recipe:
        await session.send_line("Nothing happens.")
        return
    raw = (args or "").strip().lower()
    if not raw:
        await session.send_line("Cut what?")
        return
    m = re.match(r"^(arrows?)\s+from\s+(?:my\s+)?(.+?)\s+with\s+(?:my\s+)?(.+)$", raw)
    if m:
        projectile, wood_name, tool_name = m.groups()
        if not projectile.startswith("arrow"):
            await session.send_line("Only starter arrows are supported right now.")
            return
        await _rough_shafts(session, server, cfg, recipe, wood_name, tool_name)
        return
    m = re.match(r"^nocks?\s+in\s+(?:my\s+)?(.+?)\s+with\s+(?:my\s+)?(.+)$", raw)
    if m:
        await _cut_nocks(session, server, recipe, m.group(1), m.group(2))
        return
    m = re.match(r"^(?:my\s+)?(.+?)\s+with\s+(?:my\s+)?(.+)$", raw)
    if m:
        await _work_shaft(session, server, recipe, m.group(1), m.group(2))
        return
    await session.send_line("You are not sure how to cut that for fletching.")


async def cmd_measure(session, cmd, args, server):
    cfg = _cfg(server)
    recipe = _recipe(cfg)
    if not cfg or not recipe:
        await session.send_line("Nothing happens.")
        return
    raw = (args or "").strip().lower()
    m = re.match(r"^(?:my\s+)?(.+?)\s+with\s+(?:my\s+)?(.+)$", raw)
    if not m:
        await session.send_line("Usage: MEASURE MY SHAFT WITH MY BOW")
        return
    await _measure_shaft(session, server, recipe, m.group(1), m.group(2))


async def handle_special_put(session, args, server):
    cfg = _cfg(server)
    recipe = _recipe(cfg)
    if not cfg or not recipe:
        return False
    raw = (args or "").strip().lower()
    if " on " not in raw:
        return False
    left, right = raw.split(" on ", 1)
    left = left[3:] if left.startswith("my ") else left
    right = right[3:] if right.startswith("my ") else right
    item, _ = _find_in_hands(session, left)
    target, _ = _find_in_hands(session, right)
    if not item or not target:
        return False
    if _is_glue(item, recipe) and _is_shaft(target, recipe):
        await _glue_shaft(session, server, recipe, left, right)
        return True
    if _is_fletching(item, recipe) and _is_shaft(target, recipe):
        await _fletch_shaft(session, server, recipe, left, right)
        return True
    return False
