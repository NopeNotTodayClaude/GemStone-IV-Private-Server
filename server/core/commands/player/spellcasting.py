"""
Spellcasting command bridge.

Routes player spell verbs into the Lua spell engine while keeping spell data and
effect logic in Lua.
"""

import logging
import re
import time

from server.core.protocol.colors import colorize, roundtime_msg, TextPresets, healing_msg, combat_death
from server.core.engine.magic_effects import apply_roundtime_effects, get_active_buff_totals, is_visible_to

log = logging.getLogger(__name__)


def _is_silenced(session, server) -> bool:
    status = getattr(server, "status", None)
    if status and status.has(session, "silenced"):
        return True
    buffs = _active_buff_totals(session, server)
    return bool(buffs.get("silenced"))


def _is_revival_shrouded(session, server) -> bool:
    status = getattr(server, "status", None)
    return bool(status and status.has(session, "revival_shroud"))


def _get_spell_engine(server):
    lua = getattr(server, "lua", None)
    if not lua or not lua.engine:
        return None, None
    try:
        return lua.engine, lua.engine.require("globals/magic/spell_engine")
    except Exception as e:
        log.error("spellcasting: failed to load Lua spell engine: %s", e, exc_info=True)
        return lua.engine, None


def _lua_returns(raw):
    if isinstance(raw, tuple):
        return raw
    return (raw,)


def _active_buff_totals(session, server=None):
    if not server:
        return {}
    return get_active_buff_totals(server, session)


def _equipped_armor_asg(session, server=None):
    asg = 1
    for item in getattr(session, "inventory", []) or []:
        if item.get("item_type") == "armor" and item.get("slot"):
            try:
                asg = max(asg, int(item.get("armor_asg") or 1))
            except (TypeError, ValueError):
                pass
    buffs = _active_buff_totals(session, server)
    override = int(buffs.get("armor_asg_override", 0) or 0)
    if override > asg:
        asg = override
    return asg


def _session_to_spell_entity(session, server=None):
    room_id = session.current_room.id if getattr(session, "current_room", None) else 0
    return {
        "id": int(getattr(session, "character_id", 0) or 0),
        "name": getattr(session, "character_name", "someone") or "someone",
        "level": int(getattr(session, "level", 1) or 1),
        "profession_id": int(getattr(session, "profession_id", 0) or 0),
        "race_id": int(getattr(session, "race_id", 12) or 12),
        "health_current": int(getattr(session, "health_current", 0) or 0),
        "health_max": int(getattr(session, "health_max", 0) or 0),
        "mana_current": int(getattr(session, "mana_current", 0) or 0),
        "mana_max": int(getattr(session, "mana_max", 0) or 0),
        "spirit_current": int(getattr(session, "spirit_current", 0) or 0),
        "spirit_max": int(getattr(session, "spirit_max", 0) or 0),
        "stamina_current": int(getattr(session, "stamina_current", 0) or 0),
        "stamina_max": int(getattr(session, "stamina_max", 0) or 0),
        "silver": int(getattr(session, "silver", 0) or 0),
        "position": getattr(session, "stance", "neutral") or "neutral",
        "stance": getattr(session, "stance", "neutral") or "neutral",
        "current_room_id": int(room_id or 0),
        "torso_armor_asg": _equipped_armor_asg(session, server),
        "in_sanctuary": bool(getattr(getattr(session, "current_room", None), "is_sanctuary", False)),
        "stat_strength": int(getattr(session, "stat_strength", 50) or 50),
        "stat_constitution": int(getattr(session, "stat_constitution", 50) or 50),
        "stat_dexterity": int(getattr(session, "stat_dexterity", 50) or 50),
        "stat_agility": int(getattr(session, "stat_agility", 50) or 50),
        "stat_discipline": int(getattr(session, "stat_discipline", 50) or 50),
        "stat_aura": int(getattr(session, "stat_aura", 50) or 50),
        "stat_logic": int(getattr(session, "stat_logic", 50) or 50),
        "stat_intuition": int(getattr(session, "stat_intuition", 50) or 50),
        "stat_wisdom": int(getattr(session, "stat_wisdom", 50) or 50),
        "stat_influence": int(getattr(session, "stat_influence", 50) or 50),
    }


def _player_target_entity(target_session, server=None):
    entity = _session_to_spell_entity(target_session, server)
    entity["ranged_ds"] = 0
    entity["ds_bolt"] = 0
    entity["td"] = 0
    return entity


def _creature_to_spell_entity(creature):
    ranged_ds = int(creature.get_ranged_ds() if hasattr(creature, "get_ranged_ds") else (getattr(creature, "ds_ranged", 0) or 0))
    bolt_ds = int(creature.get_bolt_ds() if hasattr(creature, "get_bolt_ds") else (getattr(creature, "ds_bolt", 0) or 0))
    return {
        "id": int(getattr(creature, "id", 0) or 0),
        "name": getattr(creature, "name", "creature") or "creature",
        "level": int(getattr(creature, "level", 1) or 1),
        "race_id": 12,
        "position": getattr(creature, "stance", "neutral") or "neutral",
        "stance": getattr(creature, "stance", "neutral") or "neutral",
        "current_room_id": int(getattr(creature, "current_room_id", 0) or 0),
        "torso_armor_asg": int(getattr(creature, "armor_asg", 1) or 1),
        "ranged_ds": ranged_ds,
        "ds_bolt": bolt_ds,
        "td": int(getattr(creature, "td", 0) or 0),
        "stat_strength": 50,
        "stat_constitution": 50,
        "stat_dexterity": 50,
        "stat_agility": 50,
        "stat_discipline": 50,
        "stat_aura": 50,
        "stat_logic": 50,
        "stat_intuition": 50,
        "stat_wisdom": 50,
        "stat_influence": 50,
    }


def _resolve_room_target(session, server, target_name):
    room = getattr(session, "current_room", None)
    if not room or not target_name:
        return None

    target_name = target_name.strip().lower()
    self_aliases = {
        "self",
        "me",
        str(getattr(session, "character_name", "") or "").strip().lower(),
    }
    if target_name in self_aliases:
        return session

    for player in server.world.get_players_in_room(room.id):
        if player is session:
            continue
        pname = (getattr(player, "character_name", "") or "").lower()
        if pname.startswith(target_name) and is_visible_to(server, session, player):
            return player

    if hasattr(server, "creatures"):
        creature = server.creatures.find_creature_in_room(room.id, target_name)
        if creature and getattr(creature, "alive", True):
            return creature

    return None


def _resolve_default_target(session):
    target = getattr(session, "target", None)
    if not target:
        return None
    room = getattr(session, "current_room", None)
    if not room:
        return None
    if hasattr(target, "current_room") and getattr(target.current_room, "id", None) == room.id:
        return target
    if getattr(target, "current_room_id", None) == room.id:
        return target
    return None


def _target_to_entity(target, server=None):
    if target is None:
        return None
    if hasattr(target, "character_id"):
        return _player_target_entity(target, server)
    return _creature_to_spell_entity(target)


def _split_spell_and_target(session, server, args):
    parts = (args or "").strip().split()
    if len(parts) < 2:
        return (args or "").strip(), None

    max_target_words = min(3, len(parts) - 1)
    for target_words in range(max_target_words, 0, -1):
        target_phrase = " ".join(parts[-target_words:])
        target_obj = _resolve_room_target(session, server, target_phrase)
        if target_obj:
            spell_arg = " ".join(parts[:-target_words]).strip()
            if spell_arg:
                return spell_arg, target_obj

    return (args or "").strip(), None


def _prepared_scroll_state(session):
    state = getattr(session, "prepared_spell", None)
    if state:
        return state
    return getattr(session, "_prepared_spell", None)


def _clear_prepared_scroll_state(session):
    session.prepared_spell = None
    if hasattr(session, "_prepared_spell"):
        session._prepared_spell = None
    if hasattr(session, "_prepared_lua_spell_number"):
        session._prepared_lua_spell_number = None


def _lookup_spell_number(server, spell_arg):
    text = (spell_arg or "").strip()
    if not text:
        return None
    numeric = int(text) if text.isdigit() else None
    if numeric is not None:
        return numeric
    db = getattr(server, "db", None)
    if not db:
        return None
    try:
        rows = db.execute_query(
            "SELECT spell_number FROM spells WHERE UPPER(mnemonic)=UPPER(%s) OR UPPER(name)=UPPER(%s) LIMIT 1",
            (text, text),
        )
    except Exception:
        return None
    if not rows:
        return None
    row = rows[0]
    if isinstance(row, dict):
        return int(row.get("spell_number") or 0) or None
    if isinstance(row, (tuple, list)) and row:
        return int(row[0] or 0) or None
    return None


def _spellbook_entry(session, spell_number):
    try:
        spell_number = int(spell_number or 0)
    except Exception:
        return None
    if spell_number <= 0:
        return None
    for row in (getattr(session, "spellbook", []) or []):
        if not isinstance(row, dict):
            continue
        try:
            if int(row.get("spell_number", 0) or 0) == spell_number:
                return row
        except Exception:
            continue
    return None


def _spell_help_text(session, spell_number):
    row = _spellbook_entry(session, spell_number)
    if not row:
        return ""
    description = str(row.get("description") or "").strip()
    if not description:
        return ""
    mana_cost = int(row.get("mana_cost", 0) or 0)
    spell_type = str(row.get("spell_type") or "spell").strip().title()
    cast_rt = int(row.get("cast_roundtime", 0) or 0)
    stats = [f"Mana {mana_cost}", spell_type]
    if cast_rt > 0:
        stats.append(f"RT {cast_rt}s")
    return f"  {description} ({' | '.join(stats)})"


def _is_healing_spell(session, spell_number):
    row = _spellbook_entry(session, spell_number) or {}
    return str(row.get("spell_type") or "").strip().lower() == "healing"


def _healing_room_message(session, target, message):
    text = str(message or "").strip()
    if not text:
        return ""
    if target is session or target is None:
        return text.replace("into you", f"into {session.character_name}", 1)
    tname = getattr(target, "character_name", None)
    if tname:
        return text.replace("into you", f"into {tname}", 1)
    return text


async def _broadcast_healing_spell(session, server, spell_number, target, message):
    if not _is_healing_spell(session, spell_number):
        return
    room = getattr(session, "current_room", None)
    if not room:
        return
    line = _healing_room_message(session, target, message)
    if not line:
        return
    await server.world.broadcast_to_room(
        room.id,
        healing_msg(f"  {line}"),
        exclude=session,
    )


_WOUND_GROUPS = {
    1102: ("right_arm", "left_arm", "right_hand", "left_hand", "right_leg", "left_leg"),
    1103: ("chest", "abdomen", "back", "nervous_system"),
    1104: ("head", "neck", "right_eye", "left_eye"),
    1105: ("chest", "abdomen", "back", "nervous_system"),
    1111: ("right_arm", "left_arm", "right_hand", "left_hand", "right_leg", "left_leg"),
    1112: ("chest", "abdomen", "back", "nervous_system"),
    1113: ("head", "neck", "right_eye", "left_eye"),
    1114: ("chest", "abdomen", "back", "nervous_system"),
}


def _pick_spell_heal_location(target_session, spell_number):
    wounds = getattr(target_session, "wounds", {}) or {}
    groups = _WOUND_GROUPS.get(spell_number, ())
    if not groups:
        return None
    scars_only = spell_number in (1111, 1112, 1113, 1114)
    candidates = []
    for loc in groups:
        entry = wounds.get(loc)
        if not isinstance(entry, dict):
            continue
        wound_rank = int(entry.get("wound_rank", 0) or 0)
        scar_rank = int(entry.get("scar_rank", 0) or 0)
        if scars_only:
            score = scar_rank
            if score > 0:
                candidates.append((score, loc))
        else:
            score = wound_rank
            if score > 0:
                candidates.append((score, loc))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


async def _apply_post_cast_side_effects(session, server, spell_number, target_obj, verb="cast"):
    bridge = getattr(server, "wound_bridge", None)
    if not bridge:
        return ""

    target_session = target_obj if hasattr(target_obj, "character_id") else session
    extra_lines = []

    if spell_number in _WOUND_GROUPS:
        loc = _pick_spell_heal_location(target_session, spell_number)
        if loc:
            result = bridge.empath_heal(session, target_session, loc)
            if result.get("ok"):
                try:
                    await bridge.save_wounds(target_session)
                except Exception:
                    pass
                msg = (result.get("message") or "").strip()
                if msg:
                    extra_lines.append(msg)

    if spell_number == 1140:
        loc = None
        wounds = getattr(target_session, "wounds", {}) or {}
        ranked = []
        for loc_key, entry in wounds.items():
            if isinstance(entry, dict):
                ranked.append((max(int(entry.get("wound_rank", 0) or 0), int(entry.get("scar_rank", 0) or 0)), loc_key))
        ranked = [item for item in ranked if item[0] > 0]
        if ranked:
            ranked.sort(reverse=True)
            loc = ranked[0][1]
        if loc:
            result = bridge.empath_heal(session, target_session, loc)
            if result.get("ok"):
                try:
                    await bridge.save_wounds(target_session)
                except Exception:
                    pass
                msg = (result.get("message") or "").strip()
                if msg:
                    extra_lines.append(msg)

    if spell_number == 1150:
        wounds = getattr(target_session, "wounds", {}) or {}
        ranked = []
        for loc_key, entry in wounds.items():
            if isinstance(entry, dict):
                ranked.append((max(int(entry.get("wound_rank", 0) or 0), int(entry.get("scar_rank", 0) or 0)), loc_key))
        ranked = [item for item in ranked if item[0] > 0]
        if ranked:
            ranked.sort(reverse=True)
            for _, loc in ranked[:2]:
                result = bridge.empath_heal(session, target_session, loc)
                if result.get("ok"):
                    msg = (result.get("message") or "").strip()
                    if msg:
                        extra_lines.append(msg)
            try:
                await bridge.save_wounds(target_session)
            except Exception:
                pass

    return ("\n" + "\n".join(extra_lines)) if extra_lines else ""


def _apply_lua_char_updates(engine, lua_char, session):
    try:
        updated = engine.lua_to_python(lua_char)
    except Exception:
        updated = None
    if isinstance(updated, dict) and "mana_current" in updated:
        session.mana_current = int(updated.get("mana_current") or 0)


def _refresh_spell_resources(target_session, server):
    if not getattr(server, "db", None) or not getattr(target_session, "character_id", None):
        return
    try:
        rows = server.db.execute_query(
            """
            SELECT health_current, health_max, mana_current, mana_max,
                   spirit_current, spirit_max, stamina_current, stamina_max, silver, current_room_id
            FROM characters
            WHERE id = %s
            LIMIT 1
            """,
            (target_session.character_id,),
        )
    except Exception:
        return
    if not rows:
        return
    row = rows[0]
    attrs = (
        "health_current", "health_max",
        "mana_current", "mana_max",
        "spirit_current", "spirit_max",
        "stamina_current", "stamina_max",
        "silver",
    )
    room_id = None
    if isinstance(row, dict):
        for attr in attrs:
            if attr in row and row[attr] is not None:
                setattr(target_session, attr, int(row[attr] or 0))
        room_id = int(row.get("current_room_id") or 0) if row.get("current_room_id") is not None else None
    elif isinstance(row, (tuple, list)):
        for idx, attr in enumerate(attrs):
            if idx < len(row) and row[idx] is not None:
                setattr(target_session, attr, int(row[idx] or 0))
        if len(row) > len(attrs) and row[len(attrs)] is not None:
            room_id = int(row[len(attrs)] or 0)
    if room_id and getattr(server, "world", None):
        current_room = getattr(target_session, "current_room", None)
        current_room_id = int(getattr(current_room, "id", 0) or 0)
        if room_id != current_room_id:
            new_room = server.world.get_room(room_id)
            if new_room:
                if current_room_id:
                    server.world.remove_player_from_room(target_session, current_room_id)
                target_session.previous_room = current_room
                target_session.current_room = new_room
                server.world.add_player_to_room(target_session, new_room.id)


def _refresh_post_spell_state(session, server, target_obj=None):
    _refresh_spell_resources(session, server)
    if hasattr(target_obj, "character_id") and target_obj is not session:
        _refresh_spell_resources(target_obj, server)
    try:
        session.fame = int(server.db.get_character_fame(session.character_id) or 0)
    except Exception:
        pass


def _cast_roundtime(prepared_state=None):
    if prepared_state and int(prepared_state.get("number") or 0) == 1700:
        return 5
    return 3


def _spell_cast_roundtime(session, server, spell_number, prepared_state=None):
    base_rt = _cast_roundtime(prepared_state)
    row = _spellbook_entry(session, spell_number)
    is_bolt = str((row or {}).get("spell_type") or "").strip().lower() == "bolt"
    return apply_roundtime_effects(base_rt, server, session, is_bolt=is_bolt)


async def cmd_send(session, cmd, args, server):
    """SEND <amount> TO <target> - Share mana using the matching mana control skill."""
    text = (args or "").strip()
    if not text:
        await session.send_line("Send how much mana to whom?")
        return

    match = re.match(r"^(?P<amount>\d+)\s+to\s+(?P<target>.+)$", text, re.IGNORECASE)
    if not match:
        match = re.match(r"^(?P<target>.+?)\s+(?P<amount>\d+)$", text, re.IGNORECASE)
    if not match:
        await session.send_line("Usage: SEND <amount> TO <person>")
        return

    amount = int(match.group("amount") or 0)
    target_name = (match.group("target") or "").strip()
    if amount <= 0:
        await session.send_line("You must send at least 1 mana.")
        return
    if amount > int(getattr(session, "mana_current", 0) or 0):
        await session.send_line("You do not have that much mana to send.")
        return

    target = _resolve_room_target(session, server, target_name)
    if not target or not hasattr(target, "character_id"):
        await session.send_line(f"You do not see any player here matching '{target_name}'.")
        return
    if target is session:
        await session.send_line("You are already carrying your own mana.")
        return

    if int(getattr(target, "mana_current", 0) or 0) >= int(getattr(target, "mana_max", 0) or 0):
        await session.send_line(f"{target.character_name} cannot accept any more mana right now.")
        return

    engine, _spell_engine = _get_spell_engine(server)
    if not engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    try:
        mana_mod = engine.require("globals/magic/mana_system")
        ranks = getattr(session, "skills", {}) or {}
        sender_prof = int(getattr(session, "profession_id", 0) or 0)
        target_prof = int(getattr(target, "profession_id", 0) or 0)

        sphere_by_prof = {
            3: "elemental", 4: "spirit", 5: "spirit", 6: "spirit",
            7: "spirit", 8: "mental", 9: "spirit", 10: "mental",
        }
        preferred = sphere_by_prof.get(sender_prof) or sphere_by_prof.get(target_prof) or "spirit"
        skill_id = {"elemental": 19, "spirit": 20, "mental": 21}[preferred]

        sender_skill = ranks.get(skill_id, {}) if isinstance(ranks, dict) else {}
        receiver_skill = (getattr(target, "skills", {}) or {}).get(skill_id, {})
        sender_bonus = int(sender_skill.get("bonus", 0) or 0) if isinstance(sender_skill, dict) else 0
        receiver_bonus = int(receiver_skill.get("bonus", 0) or 0) if isinstance(receiver_skill, dict) else 0

        actual = int(engine.call_hook(mana_mod, "calc_sharing", amount, sender_bonus, receiver_bonus) or 0)
    except Exception as e:
        log.error("SEND failed to use Lua mana sharing: %s", e, exc_info=True)
        await session.send_line("Mana sharing is unavailable right now.")
        return

    actual = max(0, min(actual, int(getattr(target, "mana_max", 0) or 0) - int(getattr(target, "mana_current", 0) or 0)))
    if actual <= 0:
        await session.send_line("The mana dissipates before your target can benefit from it.")
        return

    session.mana_current = max(0, int(session.mana_current) - amount)
    target.mana_current = min(int(target.mana_max or 0), int(target.mana_current or 0) + actual)

    if getattr(server, "db", None):
        try:
            server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver,
            )
            server.db.save_character_resources(
                target.character_id,
                target.health_current, target.mana_current,
                target.spirit_current, target.stamina_current,
                target.silver,
            )
        except Exception:
            pass

    loss = max(0, amount - actual)
    await session.send_line(colorize(
        f"You send {amount} mana to {target.character_name}, who receives {actual} mana"
        + (f" after {loss} mana bleeds away." if loss else "."),
        TextPresets.SYSTEM,
    ))
    await target.send_line(colorize(
        f"{session.character_name} sends you {actual} mana.",
        TextPresets.SYSTEM,
    ))
    if getattr(server, "guild", None):
        try:
            await server.guild.record_event(session, "mana_share_success")
        except Exception:
            pass
    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_prepare(session, cmd, args, server):
    if _is_revival_shrouded(session, server):
        await session.send_line(colorize("  You are still wrapped in revival starlight and cannot shape an attack yet.", TextPresets.WARNING))
        return
    if _is_silenced(session, server):
        await session.send_line(colorize("  You are silenced and cannot shape the words of a spell.", TextPresets.WARNING))
        return
    spell_arg = (args or "").strip()
    if not spell_arg:
        await session.send_line("Prepare which spell?")
        return

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session, server))
    raw = engine.call_hook(spell_engine, "prepare", raw_char, spell_arg)
    ok, message = _lua_returns(raw)[:2]
    if ok:
        _clear_prepared_scroll_state(session)
        session._prepared_lua_spell_number = _lookup_spell_number(server, spell_arg)
        await session.send_line(colorize(f"  {message}", TextPresets.SYSTEM))
        help_text = _spell_help_text(session, session._prepared_lua_spell_number)
        if help_text:
            await session.send_line(colorize(help_text, TextPresets.NPC_EMOTE))
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
    else:
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))


async def cmd_release(session, cmd, args, server):
    prepared = _prepared_scroll_state(session)
    if prepared:
        spell_name = prepared.get("name") or f"spell {prepared.get('number', '?')}"
        _clear_prepared_scroll_state(session)
        await session.send_line(colorize(f"  You release the {spell_name} spell.", TextPresets.SYSTEM))
        return

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session, server))
    raw = engine.call_hook(spell_engine, "release", raw_char)
    ok, message = _lua_returns(raw)[:2]
    if ok:
        session._prepared_lua_spell_number = None
    preset = TextPresets.SYSTEM if ok else TextPresets.WARNING
    await session.send_line(colorize(f"  {message}", preset))


def _lua_result_to_dict(engine, values):
    """Safely extract the Lua result table (values[2]) as a plain Python dict."""
    if not values or len(values) < 3 or values[2] is None:
        return {}
    try:
        converted = engine.lua_to_python(values[2])
        if isinstance(converted, dict):
            return converted
    except Exception:
        pass
    return {}


async def _apply_spell_damage(session, server, target, result_dict):
    """
    Apply damage propagated from Lua via ctx.result.damage / ctx.result.room_damage
    to the actual target creature(s) or player, with full crit/wound pipeline
    matching the melee combat system.
    """
    if not result_dict:
        return

    import random as _random
    damage           = int(result_dict.get('damage')           or 0)
    room_damage      = int(result_dict.get('room_damage')      or 0)
    knocked_down     = bool(result_dict.get('knocked_down'))
    room_undead_only = bool(result_dict.get('room_undead_only'))
    room_max_targets = int(result_dict.get('room_max_targets') or 0)
    # damage_type hint from Lua (e.g. 'heat', 'cold', 'plasma').  Falls back to 'magic'.
    damage_type      = (result_dict.get('damage_type') or 'magic').lower()

    from server.core.engine.combat.combat_engine import (
        _record_town_trouble_damage, _record_town_trouble_kill,
        CRIT_MESSAGES, LETHAL_THRESHOLDS, SEVERABLE_LOCATIONS,
        LOCATION_CRIT_DIV_MULT,
    )
    from server.core.scripting.loaders.body_types_loader import random_location
    from server.core.protocol.colors import combat_damage, combat_crit

    # Spell crit divisor — spells bypass physical armour; use a fixed per-type base.
    # GS4: elemental spells drive crits through spell rank, not armour piercing.
    # We approximate: every 20 HP of spell damage = 1 crit rank (caps at 9).
    SPELL_CRIT_DIVISOR = 20

    def _spell_crit(dmg, creature):
        """Compute crit rank for a spell hit.  Returns (rank, location)."""
        body_type = getattr(creature, 'body_type', 'humanoid') or 'humanoid'
        location  = random_location(body_type)
        loc_mult  = LOCATION_CRIT_DIV_MULT.get(location, 1.0)
        divisor   = max(1, int(SPELL_CRIT_DIVISOR * loc_mult))
        rank_max  = min(9, dmg // divisor)
        if rank_max <= 0:
            return 0, location
        rank = _random.randint(max(1, (rank_max + 1) // 2), rank_max)
        return rank, location

    async def _apply_creature_hit(creature, dmg):
        """Full hit pipeline: damage → crit → wound → death."""
        actual = creature.take_damage(dmg)
        _record_town_trouble_damage(server, session, creature, actual)

        if knocked_down and not creature.is_dead and hasattr(creature, 'prone'):
            creature.prone = True

        # ── Crit / wound ──────────────────────────────────────────────────
        crit_rank, location = _spell_crit(actual, creature)
        await session.send_line(combat_damage(actual, location))
        if crit_rank > 0:
            crit_msgs = CRIT_MESSAGES.get(damage_type, CRIT_MESSAGES['magic'])
            await session.send_line(combat_crit(crit_rank, crit_msgs.get(crit_rank, 'Critical hit!')))
        if crit_rank >= 1 and hasattr(creature, 'apply_wound'):
            old_sev = creature.wounds.get(location, 0) if hasattr(creature, 'wounds') else 0
            new_sev = creature.apply_wound(location, crit_rank)
            if new_sev > old_sev and hasattr(creature, 'evaluate_combat_impairment'):
                impairment = creature.evaluate_combat_impairment(location, old_sev, new_sev)
                if impairment.get('dropped_weapon'):
                    await session.send_line(colorize(
                        f'  {creature.full_name.capitalize()} drops its weapon!',
                        TextPresets.COMBAT_HIT,
                    ))
                if impairment.get('severed') and location in SEVERABLE_LOCATIONS:
                    await session.send_line(colorize(
                        f'  The spell severs {creature.full_name}\'s {location}!',
                        TextPresets.COMBAT_HIT,
                    ))
                if impairment.get('stance_shift'):
                    creature.stance = impairment['stance_shift']

        # ── Death check ───────────────────────────────────────────────────
        if creature.is_dead or crit_rank >= LETHAL_THRESHOLDS.get(location, 99):
            if not creature.is_dead:
                creature.take_damage(creature.health_current)
            await session.send_line(combat_death(creature.full_name.capitalize()))
            if getattr(server, 'world', None):
                await server.world.broadcast_to_room(
                    session.current_room.id,
                    f'  {creature.full_name.capitalize()} falls to the ground dead!',
                    exclude=session,
                )
            server.creatures.mark_dead(creature)
            await _record_town_trouble_kill(server, session, creature)
            if session.target is creature:
                session.target = None
            remaining = [
                c for c in server.creatures.get_creatures_in_room(session.current_room.id)
                if c.alive and c.aggressive
            ]
            if not remaining:
                from server.core.engine.combat.combat_engine import _exit_combat
                _exit_combat(server, session)
            if hasattr(server, 'experience'):
                from server.core.commands.player.party import award_party_kill_xp
                await award_party_kill_xp(session, creature, server)
            return True  # killed
        return False  # still alive

    # ── Single-target ──────────────────────────────────────────────────────
    if damage > 0 and target is not None:
        if hasattr(target, 'take_damage'):
            # Creature
            await _apply_creature_hit(target, damage)
        elif hasattr(target, 'health_current') and hasattr(target, 'character_id'):
            # Player target (e.g. PvP or AoE hitting self)
            new_hp = max(0, int(getattr(target, 'health_current', 0) or 0) - damage)
            target.health_current = new_hp
            if getattr(server, 'db', None) and getattr(target, 'character_id', None):
                server.db.execute(
                    'UPDATE characters SET health_current=? WHERE id=?',
                    [new_hp, target.character_id],
                )

    # ── Room-wide ──────────────────────────────────────────────────────────
    if room_damage > 0 and getattr(session, 'current_room', None):
        creatures = list(server.creatures.get_creatures_in_room(session.current_room.id))
        hit_count = 0
        for c in creatures:
            if not c.alive:
                continue
            if room_undead_only and not getattr(c, 'is_undead', False):
                continue
            if room_max_targets and hit_count >= room_max_targets:
                break
            await _apply_creature_hit(c, room_damage)
            hit_count += 1
        remaining = [
            c for c in server.creatures.get_creatures_in_room(session.current_room.id)
            if c.alive and c.aggressive
        ]
        if not remaining:
            from server.core.engine.combat.combat_engine import _exit_combat
            _exit_combat(server, session)


async def cmd_cast(session, cmd, args, server):
    if _is_revival_shrouded(session, server):
        await session.send_line(colorize("  You are still wrapped in revival starlight and cannot cast yet.", TextPresets.WARNING))
        return
    if _is_silenced(session, server):
        await session.send_line(colorize("  You are silenced and cannot cast.", TextPresets.WARNING))
        return
    target = None
    if (args or "").strip():
        target = _resolve_room_target(session, server, args.strip())
        if not target:
            await session.send_line(f"You don't see '{args.strip()}' here.")
            return
    else:
        target = _resolve_default_target(session)

    prepared = _prepared_scroll_state(session)
    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session, server))
    raw_target = engine.python_to_lua(_target_to_entity(target, server)) if target else None
    verb = (cmd or "cast").strip().lower()

    if prepared:
        spell_number = int(prepared.get("number") or 0)
        raw = engine.call_hook(
            spell_engine,
            "cast_direct",
            raw_char,
            raw_target,
            spell_number,
            verb,
            None,
            True,
        )
        values = _lua_returns(raw)
        ok = bool(values[0]) if values else False
        message = values[1] if len(values) > 1 else "The spell fizzles."
        if ok:
            _clear_prepared_scroll_state(session)
            result_dict = _lua_result_to_dict(engine, values)
            await _apply_spell_damage(session, server, target, result_dict)
            message = f"{message}{await _apply_post_cast_side_effects(session, server, spell_number, target, verb)}"
            _apply_lua_char_updates(engine, raw_char, session)
            _refresh_post_spell_state(session, server, target)
            if _is_healing_spell(session, spell_number):
                await session.send_line(healing_msg(f"  {message}"))
                await _broadcast_healing_spell(session, server, spell_number, target, message)
            else:
                _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM
                await session.send_line(colorize(f"  {message}", _spell_color))
            if getattr(server, "guild", None):
                try:
                    await server.guild.record_event(session, "spell_cast_success")
                except Exception:
                    pass
            rt = _spell_cast_roundtime(session, server, spell_number, prepared)
            session.set_roundtime(rt)
            await session.send_line(roundtime_msg(rt))
        else:
            await session.send_line(colorize(f"  {message}", TextPresets.WARNING))
        return

    spell_number = int(getattr(session, "_prepared_lua_spell_number", 0) or 0)
    raw = engine.call_hook(spell_engine, "cast", raw_char, raw_target, verb)
    values = _lua_returns(raw)
    ok = bool(values[0]) if values else False
    message = values[1] if len(values) > 1 else "The spell fizzles."
    result_dict = _lua_result_to_dict(engine, values)
    _apply_lua_char_updates(engine, raw_char, session)
    if ok:
        await _apply_spell_damage(session, server, target, result_dict)
        message = f"{message}{await _apply_post_cast_side_effects(session, server, spell_number, target, verb)}"
        _refresh_post_spell_state(session, server, target)
        session._prepared_lua_spell_number = None
        if _is_healing_spell(session, spell_number):
            await session.send_line(healing_msg(f"  {message}"))
            await _broadcast_healing_spell(session, server, spell_number, target, message)
        else:
            _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM
            await session.send_line(colorize(f"  {message}", _spell_color))
        if getattr(server, "guild", None):
            try:
                await server.guild.record_event(session, "spell_cast_success")
            except Exception:
                pass
        rt = _spell_cast_roundtime(session, server, spell_number, prepared)
        session.set_roundtime(rt)
        await session.send_line(roundtime_msg(rt))
    else:
        session._prepared_lua_spell_number = None
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))


async def cmd_incant(session, cmd, args, server):
    if _is_revival_shrouded(session, server):
        await session.send_line(colorize("  You are still wrapped in revival starlight and cannot incant yet.", TextPresets.WARNING))
        return
    if _is_silenced(session, server):
        await session.send_line(colorize("  You are silenced and cannot incant a spell.", TextPresets.WARNING))
        return
    spell_arg, target_obj = _split_spell_and_target(session, server, args)
    if not spell_arg:
        await session.send_line("Incant which spell?")
        return

    if not target_obj:
        target_obj = _resolve_default_target(session)

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session, server))
    raw_target = engine.python_to_lua(_target_to_entity(target_obj, server)) if target_obj else None
    spell_number = _lookup_spell_number(server, spell_arg) or 0
    raw = engine.call_hook(spell_engine, "incant", raw_char, spell_arg, raw_target, "cast")
    values = _lua_returns(raw)
    ok = bool(values[0]) if values else False
    message = values[1] if len(values) > 1 else "The spell fizzles."
    result_dict = _lua_result_to_dict(engine, values)
    _apply_lua_char_updates(engine, raw_char, session)
    if ok:
        await _apply_spell_damage(session, server, target_obj, result_dict)
        _clear_prepared_scroll_state(session)
        message = f"{message}{await _apply_post_cast_side_effects(session, server, spell_number, target_obj, 'cast')}"
        _refresh_post_spell_state(session, server, target_obj)
        if _is_healing_spell(session, spell_number):
            await session.send_line(healing_msg(f"  {message}"))
            await _broadcast_healing_spell(session, server, spell_number, target_obj, message)
        else:
            _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM
            await session.send_line(colorize(f"  {message}", _spell_color))
        help_text = _spell_help_text(session, spell_number)
        if help_text:
            await session.send_line(colorize(help_text, TextPresets.NPC_EMOTE))
        if getattr(server, "guild", None):
            try:
                await server.guild.record_event(session, "spell_cast_success")
            except Exception:
                pass
        rt = _spell_cast_roundtime(session, server, spell_number)
        session.set_roundtime(rt)
        await session.send_line(roundtime_msg(rt))
    else:
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))
