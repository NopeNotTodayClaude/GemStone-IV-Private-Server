"""
Shop commands - LIST, ORDER, BUY, SELL, APPRAISE
GemStone IV style shop interaction.

LIST   - List items for sale in the current shop (alias for ORDER)
ORDER  - List items for sale in the current shop
BUY <item> - Purchase an item from the shop
SELL <item> - Sell an item from your hands to the shop
APPRAISE <item> - Get the sell value of an item in your hands
"""

import json
import logging
from decimal import Decimal
from server.core.protocol.colors import (
    colorize, TextPresets, roundtime_msg, npc_speech, npc_emote,
    YELLOW, CYAN, BRIGHT_CYAN, MAGENTA, BRIGHT_GREEN,
    GREEN, BRIGHT_YELLOW, BRIGHT_WHITE, WHITE, BOLD, RESET,
)
from server.core.commands.player.currency import (
    liquid_funds,
    liquid_funds_text,
    receive_hand_after_payment,
    spend_liquid_funds,
    describe_payment,
)

log = logging.getLogger(__name__)

PAWN_CATEGORIES = ("weapon", "armor", "arcana", "misc")
PAWN_TABLE_LABELS = {
    "weapon": "weapon table",
    "armor": "armor table",
    "arcana": "arcana table",
    "misc": "miscellaneous table",
}


def _parse_npc_topic(raw_args: str, *, require_topic: bool, default_topic: str = "hello"):
    raw_args = (raw_args or "").strip()
    if not raw_args:
        return None, None

    if raw_args.lower().startswith("to "):
        raw_args = raw_args[3:].strip()

    lower = raw_args.lower()
    if " about " in lower:
        idx = lower.index(" about ")
        npc_name = raw_args[:idx].strip()
        topic = raw_args[idx + 7:].strip()
    else:
        parts = raw_args.split(None, 1)
        npc_name = parts[0].strip()
        topic = parts[1].strip() if len(parts) > 1 else ""

    if require_topic and not topic:
        return npc_name, None
    return npc_name, (topic or default_topic)


def _quest_topic_key(topic: str) -> str:
    text = (topic or "").strip().lower()
    if not text:
        return ""
    chars = []
    prev_sep = False
    for ch in text:
        if ch.isalnum():
            chars.append(ch)
            prev_sep = False
        elif not prev_sep:
            chars.append("_")
            prev_sep = True
    return "".join(chars).strip("_")


async def _send_npc_response(session, npc, topic, server):
    from server.core.commands.player.movement import _move_player

    quest_engine = getattr(server, "guild", None)
    topic_key = _quest_topic_key(topic)
    if quest_engine and topic_key:
        try:
            await quest_engine.record_event(session, f"npc_topic:{npc.template_id}:{topic_key}")
        except Exception:
            log.exception("Failed recording NPC topic event for %s/%s", getattr(npc, "template_id", "unknown"), topic_key)

    try:
        from server.core.commands.player.guild import (
            get_guild_npc_response,
            get_quest_npc_response,
            maybe_handle_guild_npc_action,
            maybe_handle_adventurer_guild_npc_response,
        )
        inn_mgr = getattr(server, "inns", None)
        if inn_mgr and await inn_mgr.maybe_handle_npc_topic(session, npc, topic):
            return
        if await maybe_handle_adventurer_guild_npc_response(session, npc, topic, server):
            return
        response = npc.get_talk_response(server, session, topic)
        if isinstance(response, dict):
            justice_mgr = getattr(server, "justice", None)
            if justice_mgr and await justice_mgr.maybe_handle_npc_response(session, npc, topic, response):
                return
            travel_mgr = getattr(server, "travel_offices", None)
            if travel_mgr and await travel_mgr.maybe_handle_npc_response(session, npc, topic, response):
                return
            if await maybe_handle_guild_npc_action(session, npc, topic, response, server):
                return
            text = None
            for field in ("response", "message", "text"):
                value = response.get(field)
                if isinstance(value, str) and value.strip():
                    text = value.strip()
                    break
            if text:
                await session.send_line(npc_speech(npc.display_name, f'says, "{text}"'))

            target_room_id = int(response.get("move_to_room") or 0)
            if target_room_id:
                current_room = getattr(session, "current_room", None)
                target_room = server.world.get_room(target_room_id) if getattr(server, "world", None) else None
                if current_room and target_room:
                    direction_label = str(response.get("move_verb") or response.get("direction_label") or "out").strip() or "out"
                    await _move_player(session, current_room, target_room, direction_label, server, sneaking=False)
                else:
                    await session.send_line("That route leads nowhere right now.")
            return

        if response:
            await session.send_line(npc_speech(npc.display_name, f'says, "{response}"'))
            return

        guild_response = get_guild_npc_response(session, npc, topic, server)
        if guild_response:
            await session.send_line(npc_speech(npc.display_name, f'says, "{guild_response}"'))
            return
        quest_response = get_quest_npc_response(session, npc, topic, server)
        if quest_response:
            await session.send_line(npc_speech(npc.display_name, f'says, "{quest_response}"'))
            return
    except Exception:
        pass

    await session.send_line(f"{npc.display_name} shrugs. 'I don't know much about that.'")


def _find_shopkeeper_for_shop(server, shop_id):
    if not hasattr(server, "npcs") or not shop_id:
        return None
    for npc in server.npcs.get_all_npcs():
        if getattr(npc, "can_shop", False) and int(getattr(npc, "shop_id", 0) or 0) == int(shop_id):
            return npc
    return None


def _is_pawn_shop(shop):
    return bool(shop and str(shop.get("shop_type") or "").lower() == "pawn")


def _is_pawn_backroom_room(shop, room_id):
    return bool(shop and int(shop.get("backroom_room_id") or 0) == int(room_id or 0))


def _normalize_pawn_category(raw: str | None):
    text = str(raw or "").strip().lower()
    if not text:
        return None
    aliases = {
        "weapon": "weapon",
        "weapons": "weapon",
        "armor": "armor",
        "armour": "armor",
        "arcana": "arcana",
        "magic": "arcana",
        "misc": "misc",
        "miscellaneous": "misc",
        "table": None,
    }
    return aliases.get(text, text if text in PAWN_CATEGORIES else None)


def _pawn_category_for_item(item: dict) -> str:
    item_type = str(item.get("item_type") or "").lower()
    noun = str(item.get("noun") or "").lower()
    weapon_type = str(item.get("weapon_type") or "").lower()
    weapon_category = str(item.get("weapon_category") or "").lower()
    if item_type in {"weapon", "ammunition"} or weapon_type or weapon_category:
        return "weapon"
    if item_type in {"armor", "shield"} or item.get("armor_asg") or item.get("shield_size"):
        return "armor"
    if item_type in {"magic", "jewelry"}:
        return "arcana"
    if noun in {"scroll", "runestone", "wand", "rod", "orb", "amulet", "ring"}:
        return "arcana"
    if any(item.get(key) for key in ("spell_number", "spell_name", "charges")):
        return "arcana"
    return "misc"


def _pawn_snapshot(item: dict) -> dict:
    def _normalize(value):
        if isinstance(value, Decimal):
            return int(value) if value == value.to_integral_value() else float(value)
        if isinstance(value, dict):
            return {k: _normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_normalize(v) for v in value]
        if isinstance(value, tuple):
            return [_normalize(v) for v in value]
        return value

    return {
        key: _normalize(value)
        for key, value in dict(item or {}).items()
        if key not in {"inv_id", "slot", "container_id"}
    }


def _load_shop_by_room(server, room_id):
    if not server.db:
        return None
    rows = server.db.execute_query(
        """
        SELECT id, name, room_id, backroom_room_id, shop_type, buy_multiplier, sell_multiplier
        FROM shops
        WHERE room_id = %s OR backroom_room_id = %s
        LIMIT 1
        """,
        (room_id, room_id),
    )
    if not rows:
        return None
    row = rows[0]
    return {
        "id": row[0],
        "name": row[1],
        "room_id": row[2],
        "backroom_room_id": row[3],
        "shop_type": row[4],
        "buy_multiplier": float(row[5]),
        "sell_multiplier": float(row[6]),
    }


async def _get_shop_for_room(session, server):
    """Get the shop data for the current room. Returns (shop_dict, npc) or (None, None)."""
    room_id = session.current_room.id

    # Find shopkeeper NPC in room
    npc = None
    if hasattr(server, 'npcs'):
        npc = server.npcs.get_shopkeeper_in_room(room_id)

    shop = None
    if npc and npc.shop_id:
        shop = _load_shop(server, npc.shop_id)
    if not shop:
        shop = _load_shop_by_room(server, room_id)
        if shop and not npc:
            npc = _find_shopkeeper_for_shop(server, shop["id"])
    if not shop:
        await session.send_line("There is no shop here.")
        return None, None

    return shop, npc


def _load_shop(server, shop_id):
    """Load shop data from database."""
    if not server.db:
        return None
    rows = server.db.execute_query(
        """
        SELECT id, name, room_id, backroom_room_id, shop_type, buy_multiplier, sell_multiplier
        FROM shops
        WHERE id = %s
        """,
        (shop_id,)
    )
    if not rows:
        return None
    row = rows[0]
    return {
        "id": row[0],
        "name": row[1],
        "room_id": row[2],
        "backroom_room_id": row[3],
        "shop_type": row[4],
        "buy_multiplier": float(row[5]),
        "sell_multiplier": float(row[6]),
    }


def _load_pawn_backroom_items(server, shop_id, category=None):
    if not server.db:
        return []
    category = _normalize_pawn_category(category)
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        if category:
            cur.execute(
                """
                SELECT *
                FROM pawnshop_backroom_inventory
                WHERE shop_id = %s AND category_key = %s
                ORDER BY created_at DESC, id DESC
                """,
                (shop_id, category),
            )
        else:
            cur.execute(
                """
                SELECT *
                FROM pawnshop_backroom_inventory
                WHERE shop_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (shop_id,),
            )
        rows = cur.fetchall()
    finally:
        conn.close()

    for row in rows:
        try:
            snapshot = json.loads(row.get("item_data") or "{}")
            if not isinstance(snapshot, dict):
                snapshot = {}
        except Exception:
            snapshot = {}
        snapshot.setdefault("item_id", row.get("item_id"))
        snapshot.setdefault("name", row.get("item_name"))
        snapshot.setdefault("short_name", row.get("item_short_name"))
        snapshot.setdefault("noun", row.get("item_noun"))
        snapshot.setdefault("item_type", row.get("item_type"))
        snapshot.setdefault("value", row.get("base_value"))
        row["snapshot"] = snapshot
    return rows


def _pawn_backroom_counts(rows):
    counts = {key: 0 for key in PAWN_CATEGORIES}
    for row in rows:
        category = _normalize_pawn_category(row.get("category_key")) or "misc"
        counts[category] += 1
    return counts


def _set_pawn_context(session, shop_id, category, rows):
    session.pawn_backroom_context = {
        "shop_id": int(shop_id),
        "category": _normalize_pawn_category(category),
        "ids": [int(row["id"]) for row in rows],
    }


def _get_pawn_context(session, shop_id):
    context = getattr(session, "pawn_backroom_context", None)
    if not isinstance(context, dict):
        return None
    if int(context.get("shop_id") or 0) != int(shop_id or 0):
        return None
    return context


def _make_pawn_catalog_payload(rows):
    payload = []
    for idx, row in enumerate(rows, 1):
        snap = dict(row.get("snapshot") or {})
        payload.append({
            "idx": idx,
            "name": snap.get("name"),
            "short_name": snap.get("short_name"),
            "noun": snap.get("noun"),
            "item_type": snap.get("item_type", "misc"),
            "price": int(row.get("ask_price") or 0),
            "weight": float(snap.get("weight") or 0),
            "value": int(snap.get("value") or 0),
            "damage_factor": float(snap.get("damage_factor") or 0),
            "weapon_speed": int(snap.get("weapon_speed") or 5),
            "weapon_category": snap.get("weapon_category") or snap.get("weapon_type") or "",
            "damage_type": snap.get("damage_type") or "",
            "attack_bonus": int(snap.get("attack_bonus") or 0),
            "damage_bonus": int(snap.get("damage_bonus") or 0),
            "enchant_bonus": int(snap.get("enchant_bonus") or 0),
            "armor_asg": int(snap.get("armor_asg") or 0),
            "shield_size": snap.get("shield_size") or "",
            "shield_ds": int(snap.get("shield_ds") or 0),
            "container_capacity": int(snap.get("container_capacity") or 0),
            "level_required": int(snap.get("level_required") or 0),
            "defense_bonus": int(snap.get("defense_bonus") or 0),
            "action_penalty": int(snap.get("action_penalty") or 0),
            "spell_hindrance": int(snap.get("spell_hindrance") or 0),
            "worn_location": snap.get("worn_location") or "",
            "material": snap.get("material") or "",
            "herb_heal_type": snap.get("herb_heal_type") or snap.get("heal_type") or "",
            "herb_heal_amount": int(snap.get("herb_heal_amount") or snap.get("heal_amount") or 0),
            "description": snap.get("description") or "",
        })
    return payload


async def _show_pawn_backroom_overview(session, server, shop, npc=None):
    rows = _load_pawn_backroom_items(server=server, shop_id=shop["id"])
    counts = _pawn_backroom_counts(rows)
    _set_pawn_context(session, shop["id"], None, [])
    await session.send_line("")
    await session.send_line(colorize(f"{shop['name']} Backroom", TextPresets.ROOM_TITLE))
    await session.send_line(colorize("=" * 60, TextPresets.SYSTEM))
    if npc:
        await session.send_line(npc_speech(npc.display_name, "says, \"The back room is sorted by weapon, armor, arcana, and miscellaneous tables.\""))
    if not rows:
        await session.send_line(colorize("  The back room is currently bare.", TextPresets.SYSTEM))
    else:
        for category in PAWN_CATEGORIES:
            label = PAWN_TABLE_LABELS[category].title()
            count = counts[category]
            await session.send_line(
                f"  {colorize(label + ':', TextPresets.SYSTEM)} {count} item{'s' if count != 1 else ''}"
            )
    await session.send_line(colorize("-" * 60, TextPresets.SYSTEM))
    await session.send_line(colorize("  LOOK ON WEAPON TABLE | LOOK ON ARMOR TABLE | LOOK ON ARCANA TABLE | LOOK ON MISC TABLE", TextPresets.SYSTEM))
    await session.send_line(colorize("  ORDER BACKROOM <table> also works from the front counter.", TextPresets.SYSTEM))
    await session.send_line(colorize("  BUY BACKROOM <table> <#> to purchase a listed item.", TextPresets.SYSTEM))
    await session.send_line("")


async def _show_pawn_backroom_table(session, server, shop, category):
    category = _normalize_pawn_category(category)
    if not category:
        await session.send_line("Look on which table? Try WEAPON, ARMOR, ARCANA, or MISC.")
        return
    rows = _load_pawn_backroom_items(server, shop["id"], category)
    _set_pawn_context(session, shop["id"], category, rows)
    await session.send_line(f"\x00SHOP_CATALOG:{json.dumps(_make_pawn_catalog_payload(rows))}\x00")
    await session.send_line("")
    await session.send_line(colorize(f"{shop['name']} - {PAWN_TABLE_LABELS[category].title()}", TextPresets.ROOM_TITLE))
    await session.send_line(colorize("=" * 60, TextPresets.SYSTEM))
    if not rows:
        await session.send_line(colorize("  The table is empty right now.", TextPresets.SYSTEM))
        await session.send_line("")
        return
    await session.send_line(
        colorize(f"  {'#':<5}", TextPresets.SYSTEM)
        + colorize(f" {'Item':<35}", TextPresets.SYSTEM)
        + colorize(f" {'Price':>10}", TextPresets.SYSTEM)
    )
    await session.send_line(colorize("-" * 60, TextPresets.SYSTEM))
    for idx, row in enumerate(rows, 1):
        snap = row["snapshot"]
        name = snap.get("name") or snap.get("short_name") or "something"
        words = str(name).split(" ", 1)
        if len(words) == 2 and words[0].lower() in ("a", "an", "the", "some"):
            name = words[1]
        raw_name = name if len(name) <= 34 else name[:31] + "..."
        padding = " " * max(0, 34 - len(raw_name))
        price_str = colorize(f"{int(row.get('ask_price') or 0):>8} silver", TextPresets.ITEM_NAME)
        await session.send_line(
            f"  {colorize(str(idx), TextPresets.SYSTEM):<5} {YELLOW}{raw_name}{RESET}{padding} {price_str}"
        )
    await session.send_line(colorize("-" * 60, TextPresets.SYSTEM))
    await session.send_line(colorize(f"  BUY BACKROOM {category} {{#}} from the front room, or BUY {category} {{#}} here.", TextPresets.SYSTEM))
    await session.send_line("")


def _insert_item_into_pawn_backroom(server, shop, item, seller_name, seller_id):
    if not server.db or not _is_pawn_shop(shop):
        return
    snapshot = _pawn_snapshot(item)
    ask_price = max(1, int((snapshot.get("value") or 0) * float(shop.get("buy_multiplier") or 1.0)))
    category = _pawn_category_for_item(snapshot)
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO pawnshop_backroom_inventory
                (shop_id, item_id, item_name, item_short_name, item_noun, item_type,
                 category_key, base_value, ask_price, item_data, sold_by_character_id, sold_by_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                shop["id"],
                int(snapshot.get("item_id") or 0),
                snapshot.get("name") or snapshot.get("short_name") or "something",
                snapshot.get("short_name") or snapshot.get("name") or "something",
                snapshot.get("noun"),
                snapshot.get("item_type"),
                category,
                int(snapshot.get("value") or 0),
                ask_price,
                json.dumps(snapshot),
                seller_id,
                seller_name,
            ),
        )
        cur.execute(
            """
            SELECT id
            FROM pawnshop_backroom_inventory
            WHERE shop_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT 100000 OFFSET 100
            """,
            (shop["id"],),
        )
        overflow_ids = [row[0] for row in cur.fetchall()]
        if overflow_ids:
            placeholders = ",".join(["%s"] * len(overflow_ids))
            cur.execute(f"DELETE FROM pawnshop_backroom_inventory WHERE id IN ({placeholders})", tuple(overflow_ids))
    finally:
        conn.close()


def _restore_pawn_snapshot_to_inventory(server, character_id, snapshot, slot=None):
    item_id = int(snapshot.get("item_id") or 0)
    if not item_id:
        return None
    inv_id = server.db.add_item_to_inventory(character_id, item_id, slot=slot)
    if not inv_id:
        return None
    restored = dict(snapshot)
    restored["inv_id"] = inv_id
    restored["slot"] = slot
    restored["container_id"] = None
    extra = {
        key: value for key, value in restored.items()
        if key not in {
            "inv_id", "item_id", "name", "short_name", "noun", "article",
            "item_type", "weight", "value", "slot", "container_id",
            "description",
        }
    }
    if extra:
        server.db.save_item_extra_data(inv_id, extra)
    return restored


async def maybe_handle_pawn_backroom_look(session, target, server):
    room = getattr(session, "current_room", None)
    if not room:
        return False
    shop = _load_shop_by_room(server, room.id)
    if not _is_pawn_shop(shop):
        return False

    cleaned = str(target or "").strip().lower()
    if cleaned in {"backroom", "back room"}:
        await _show_pawn_backroom_overview(session, server, shop, _find_shopkeeper_for_shop(server, shop["id"]))
        return True

    parts = cleaned.split()
    if "table" in parts:
        for part in parts:
            category = _normalize_pawn_category(part)
            if category:
                await _show_pawn_backroom_table(session, server, shop, category)
                return True
    return False


async def _cmd_pawn_backroom(session, server, shop, npc, args):
    args = (args or "").strip()
    if not args or args.lower() in {"help", "list", "catalog"}:
        await _show_pawn_backroom_overview(session, server, shop, npc)
        return
    category = _normalize_pawn_category(args.replace("table", "").strip())
    if category:
        await _show_pawn_backroom_table(session, server, shop, category)
        return
    await session.send_line("Backroom tables are WEAPON, ARMOR, ARCANA, and MISC.")


async def _cmd_buy_from_pawn_backroom(session, server, shop, npc, args, *, room_context_only=False):
    raw = (args or "").strip()
    if not raw:
        await session.send_line("Buy what from the backroom? Try BUY BACKROOM WEAPON 1.")
        return True

    text = raw.lower().strip()
    if text.startswith("backroom "):
        text = text[9:].strip()
    elif text == "backroom":
        await session.send_line("Buy what from the backroom? Try BUY BACKROOM WEAPON 1.")
        return True
    elif room_context_only and text.startswith("backroom"):
        text = text[8:].strip()

    category = None
    numeric = None
    parts = text.split()
    if parts:
        maybe_cat = _normalize_pawn_category(parts[0])
        if maybe_cat:
            category = maybe_cat
            if len(parts) >= 2:
                if parts[1].isdigit():
                    numeric = int(parts[1])
                else:
                    text = " ".join(parts[1:])
            else:
                await session.send_line("Buy which item number from that table?")
                return True
        elif text.isdigit():
            numeric = int(text)

    target_row = None
    if category:
        rows = _load_pawn_backroom_items(server, shop["id"], category)
        _set_pawn_context(session, shop["id"], category, rows)
        if numeric is not None:
            idx = numeric - 1
            if 0 <= idx < len(rows):
                target_row = rows[idx]
        else:
            search = text.lower()
            for row in rows:
                snap = row["snapshot"]
                if search in str(snap.get("name") or "").lower() or search in str(snap.get("short_name") or "").lower() or search in str(snap.get("noun") or "").lower():
                    target_row = row
                    break
    else:
        context = _get_pawn_context(session, shop["id"])
        if numeric is not None and context and context.get("ids"):
            ctx_ids = context["ids"]
            idx = numeric - 1
            if 0 <= idx < len(ctx_ids):
                target_id = ctx_ids[idx]
                rows = _load_pawn_backroom_items(server, shop["id"], context.get("category"))
                for row in rows:
                    if int(row["id"]) == int(target_id):
                        target_row = row
                        break
        elif text:
            rows = _load_pawn_backroom_items(server, shop["id"])
            for row in rows:
                snap = row["snapshot"]
                haystacks = (
                    str(snap.get("name") or "").lower(),
                    str(snap.get("short_name") or "").lower(),
                    str(snap.get("noun") or "").lower(),
                )
                if any(text in hay for hay in haystacks):
                    target_row = row
                    break
        else:
            await session.send_line("Browse a backroom table first, or specify one: BUY BACKROOM WEAPON 1.")
            return True

    if not target_row:
        await session.send_line("That backroom item isn't available.")
        return True

    price = int(target_row.get("ask_price") or 0)
    hand_slot = receive_hand_after_payment(session, price)
    if not hand_slot:
        await session.send_line("Your hands are full! Free a hand first.")
        return True
    if liquid_funds(session) < price:
        await session.send_line(
            npc_speech(
                (npc.display_name if npc else "The pawnbroker"),
                f'says, "That costs {price} silver. You only have {liquid_funds_text(session)}."'
            )
        )
        return True

    restored = _restore_pawn_snapshot_to_inventory(server=server, character_id=session.character_id, snapshot=target_row["snapshot"], slot=hand_slot)
    if not restored:
        await session.send_line("Something went wrong retrieving that item.")
        return True

    payment = spend_liquid_funds(session, server, price)
    if not payment.get("ok"):
        if restored.get("inv_id"):
            try:
                server.db.remove_item_from_inventory(restored["inv_id"])
            except Exception:
                pass
        await session.send_line("Something went wrong with the purchase.")
        return True

    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pawnshop_backroom_inventory WHERE id = %s", (target_row["id"],))
    finally:
        conn.close()

    if hand_slot == "right_hand":
        session.right_hand = restored
    else:
        session.left_hand = restored

    server.db.save_character_resources(
        session.character_id,
        session.health_current, session.mana_current,
        session.spirit_current, session.stamina_current,
        session.silver
    )

    item_name = restored.get("name") or restored.get("short_name") or "something"
    speaker = npc.display_name if npc else "The pawnbroker"
    await session.send_line(
        npc_speech(
            speaker,
            f'{describe_payment(payment)} and produces {colorize(item_name, TextPresets.ITEM_NAME)} from the backroom.'
        )
    )
    return True


def _load_shop_inventory(server, shop_id):
    """Load all items for sale in a shop."""
    if not server.db:
        return []
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT si.id as shop_inv_id, si.item_id, si.stock,
                   i.name, i.short_name, i.noun, i.article, i.item_type,
                   i.value, i.weight, i.weapon_type, i.weapon_category,
                   i.damage_factor, i.weapon_speed, i.damage_type,
                   i.attack_bonus, i.damage_bonus, i.enchant_bonus,
                   i.armor_asg, i.shield_size, i.shield_ds,
                   i.container_capacity, i.level_required,
                   i.defense_bonus, i.action_penalty, i.spell_hindrance,
                   i.lockpick_modifier, i.worn_location,
                   i.heal_type, i.heal_rank, i.heal_amount, i.herb_roundtime,
                   i.herb_heal_type, i.herb_heal_amount,
                   i.description, i.material
            FROM shop_inventory si
            JOIN items i ON si.item_id = i.id
            WHERE si.shop_id = %s
            ORDER BY COALESCE(i.display_order, 99), i.heal_rank, i.name
        """, (shop_id,))
        return cur.fetchall()
    finally:
        conn.close()


async def cmd_order(session, cmd, args, server):
    """ORDER [#] [MATERIAL {name}] [COLOR {name}] - List catalog or select an item."""
    shop, npc = await _get_shop_for_room(session, server)
    if not shop:
        return

    args_str = (args or "").strip()
    lower_args = args_str.lower()

    if _is_pawn_shop(shop):
        if _is_pawn_backroom_room(shop, session.current_room.id) and (not args_str or lower_args == "help"):
            await _show_pawn_backroom_overview(session, server, shop, npc)
            return
        if _is_pawn_backroom_room(shop, session.current_room.id):
            room_category = _normalize_pawn_category(lower_args.replace("table", "").strip())
            if room_category:
                await _show_pawn_backroom_table(session, server, shop, room_category)
                return
        if lower_args.startswith("backroom"):
            await _cmd_pawn_backroom(session, server, shop, npc, args_str[8:].strip())
            return

    # No args — show full catalog
    if not args_str or args_str.lower() == "help":
        items = _load_shop_inventory(server, shop["id"])
        if not items:
            await session.send_line(npc_speech(npc.name, f"says, 'I'm afraid I have nothing in stock right now.'"))
            return

        buy_mult = shop["buy_multiplier"]

        # ── Hidden catalog tag for HUD (Fix 1/2) ──────────────────────
        # The HUD intercepts \x00SHOP_CATALOG:{json}\x00, populates its
        # known-items dict with state='shop' and full stats so every item
        # name in the listing becomes a clickable link with a stat popup.
        import json as _json
        catalog_payload = []
        for idx, it in enumerate(items, 1):
            catalog_payload.append({
                "idx":              idx,
                "name":             it["name"],
                "short_name":       it["short_name"],
                "noun":             it["noun"],
                "item_type":        it.get("item_type", "misc"),
                "price":            int(it["value"] * buy_mult),
                "weight":           float(it.get("weight") or 0),
                "value":            int(it.get("value") or 0),
                "damage_factor":    float(it.get("damage_factor") or 0),
                "weapon_speed":     int(it.get("weapon_speed") or 5),
                "weapon_category":  it.get("weapon_category") or it.get("weapon_type") or "",
                "damage_type":      it.get("damage_type") or "",
                "attack_bonus":     int(it.get("attack_bonus") or 0),
                "damage_bonus":     int(it.get("damage_bonus") or 0),
                "enchant_bonus":    int(it.get("enchant_bonus") or 0),
                "armor_asg":        int(it.get("armor_asg") or 0),
                "shield_size":      it.get("shield_size") or "",
                "shield_ds":        int(it.get("shield_ds") or 0),
                "container_capacity": int(it.get("container_capacity") or 0),
                "level_required":   int(it.get("level_required") or 0),
                "defense_bonus":    int(it.get("defense_bonus") or 0),
                "action_penalty":   int(it.get("action_penalty") or 0),
                "spell_hindrance":  int(it.get("spell_hindrance") or 0),
                "worn_location":    it.get("worn_location") or "",
                "material":         it.get("material") or "",
                "herb_heal_type":   it.get("herb_heal_type") or it.get("heal_type") or "",
                "herb_heal_amount": int(it.get("herb_heal_amount") or it.get("heal_amount") or 0),
                "description":      it.get("description") or "",
            })
        await session.send_line(
            f"\x00SHOP_CATALOG:{_json.dumps(catalog_payload)}\x00"
        )
        # ──────────────────────────────────────────────────────────────

        from server.core.world.material_data import is_clothing_item
        from server.core.protocol.colors import (
            YELLOW, CYAN, BRIGHT_CYAN, MAGENTA, BRIGHT_GREEN,
            GREEN, BRIGHT_YELLOW, BRIGHT_WHITE, WHITE, BOLD, RESET
        )

        # Item type → ANSI color for the name column
        _TYPE_COLOR = {
            "weapon":     YELLOW,          # gold  — most prominent
            "armor":      BRIGHT_CYAN,     # cyan
            "shield":     CYAN,            # softer cyan
            "jewelry":    MAGENTA,         # purple/pink
            "container":  BRIGHT_GREEN,    # green
            "herb":       GREEN,           # soft green
            "consumable": GREEN,
            "gem":        BRIGHT_YELLOW,   # bright gold
            "lockpick":   BRIGHT_WHITE,
        }

        await session.send_line(f"\n{colorize(shop['name'], TextPresets.ROOM_TITLE)}")
        await session.send_line(colorize("=" * 60, TextPresets.SYSTEM))
        await session.send_line(
            colorize(f"  {'#':<5}", TextPresets.SYSTEM) +
            colorize(f" {'Item':<35}", TextPresets.SYSTEM) +
            colorize(f" {'Price':>10}", TextPresets.SYSTEM)
        )
        await session.send_line(colorize("-" * 60, TextPresets.SYSTEM))

        for idx, item in enumerate(items, 1):
            price     = int(item["value"] * buy_mult)
            stock_str = f" [{item['stock']} left]" if item["stock"] >= 0 else ""
            itype_key = (item.get("item_type") or "misc").lower()
            name_col  = YELLOW  # ALL items yellow so HUD can match them as clickable

            # Strip leading article from display name (GS4 shop listings
            # never show "a", "an", "some", "the" — just the base name).
            _raw = item["name"]
            _words = _raw.split(" ", 1)
            if len(_words) == 2 and _words[0].lower() in ("a", "an", "some", "the"):
                _raw = _words[1]
            raw_name     = _raw if len(_raw) <= 34 else _raw[:31] + "..."
            colored_name = f"{name_col}{raw_name}{RESET}"
            padding      = " " * max(0, 34 - len(raw_name))

            customizable = itype_key in ("weapon", "armor", "shield", "jewelry")
            if customizable:
                cust_mark = (colorize(" ~", TextPresets.SYSTEM)
                             if is_clothing_item(item)
                             else colorize(" *", TextPresets.ITEM_NAME))
            else:
                cust_mark = ""

            price_str = colorize(f"{price:>8} silver", TextPresets.ITEM_NAME)
            await session.send_line(
                f"  {colorize(str(idx), TextPresets.SYSTEM):<5} "
                f"{colored_name}{padding} {price_str}{stock_str}{cust_mark}"
            )

        await session.send_line(colorize("-" * 60, TextPresets.SYSTEM))
        await session.send_line(
            f"  {len(items)} items available.  "
            + colorize("* = customizable material/color", TextPresets.ITEM_NAME)
            + "  "
            + colorize("~ = color only", TextPresets.SYSTEM)
        )
        await session.send_line(colorize(
            "  Click any item name, or type: ORDER # [MATERIAL {name}] [COLOR {name}]",
            TextPresets.SYSTEM
        ))
        if _is_pawn_shop(shop):
            await session.send_line(colorize(
                "  BACKROOM or ORDER BACKROOM to browse recently pawned goods.",
                TextPresets.SYSTEM
            ))
        await session.send_line("")
        return

    # Parse: ORDER [quantity of] # [MATERIAL name] [COLOR name]
    import re
    material_choice = None
    color_choice = None

    # Extract MATERIAL
    mat_match = re.search(r'\bMATERIAL\s+(\S+)', args_str, re.IGNORECASE)
    if mat_match:
        material_choice = mat_match.group(1).lower()
        args_str = args_str[:mat_match.start()].strip() + " " + args_str[mat_match.end():].strip()
        args_str = args_str.strip()

    # Extract COLOR
    col_match = re.search(r'\bCOLOR\s+(\S+)', args_str, re.IGNORECASE)
    if col_match:
        color_choice = col_match.group(1).lower()
        args_str = args_str[:col_match.start()].strip() + " " + args_str[col_match.end():].strip()
        args_str = args_str.strip()

    # Parse quantity: "2 of 3" or just "3"
    quantity = 1
    of_match = re.match(r'^(\d+)\s+of\s+(\d+)$', args_str.strip())
    if of_match:
        quantity = int(of_match.group(1))
        item_num_str = of_match.group(2)
    else:
        item_num_str = args_str.strip()

    if not item_num_str:
        await session.send_line("Order which item?  Type ORDER to see the catalog.")
        return

    items = _load_shop_inventory(server, shop["id"])
    buy_mult = shop["buy_multiplier"]
    target_item = None

    try:
        idx = int(item_num_str) - 1
        if 0 <= idx < len(items):
            target_item = items[idx]
    except ValueError:
        search = item_num_str.lower()
        for item in items:
            if search in item["name"].lower() or search in item["noun"].lower():
                target_item = item
                break

    if not target_item:
        await session.send_line(npc_speech(npc.name, f"says, 'I don't have that.  Type ORDER to see my catalog.'"))
        return

    # Build working copy of the item
    from server.core.world.material_data import (
        get_material, can_use_material,
        apply_material_to_item, apply_color_to_item, COLORS
    )
    item_copy = dict(target_item)

    # Apply material if specified
    if material_choice:
        mat = get_material(material_choice)
        if not mat:
            await session.send_line(
                f"'{material_choice}' is not a recognized material.  "
                f"Type CUSTOMIZE to see available options."
            )
            return
        ok, reason = can_use_material(session.level, material_choice)
        if not ok:
            await session.send_line(reason)
            return
        if item_copy.get("item_type") not in ("weapon", "armor", "shield", "jewelry"):
            await session.send_line(
                f"This item cannot be made from a custom material."
            )
            return
        item_copy = apply_material_to_item(item_copy, material_choice)

    # Apply color if specified
    if color_choice:
        if color_choice not in COLORS:
            await session.send_line(
                f"'{color_choice}' is not an available color.  "
                f"Valid colors include: {', '.join(COLORS[:10])}..."
            )
            return
        item_copy = apply_color_to_item(item_copy, color_choice)

    price = int(item_copy["value"] * buy_mult) * quantity

    # Store as pending order
    session._pending_order = {
        "item": item_copy,
        "shop": shop,
        "npc": npc,
        "quantity": quantity,
        "price": price,
        "material": material_choice,
        "color": color_choice,
    }
    session._customize_materials = None  # reset for CUSTOMIZE

    # Show selection info
    bonus_info = ""
    if material_choice:
        mat = get_material(material_choice)
        if mat and mat["enchant_bonus"] > 0:
            bonus_info = colorize(f"  [{mat['display']} +{mat['enchant_bonus']} enchantment]", TextPresets.ITEM_NAME)

    customizable = target_item.get("item_type") in ("weapon", "armor", "shield", "jewelry")
    cust_tip = colorize("  Type CUSTOMIZE to change material/color.", TextPresets.SYSTEM) if customizable and not material_choice else ""

    await session.send_line(
        npc_speech(npc.name, f"nods.  '{colorize(item_copy['name'], TextPresets.ITEM_NAME)}' — ")
        + f"{price:,} silver{'s' if price != 1 else ''} for {quantity}.{bonus_info}"
        + f"\n  Type BUY to purchase, or CONFIRM to review & order.{cust_tip}"
    )

    # ── Inline stat preview (Fix 2) ───────────────────────────────────────
    try:
        from server.core.commands.player.inventory import _item_stat_lines
        for stat_line in _item_stat_lines(item_copy):
            await session.send_line(stat_line)
    except Exception:
        pass


async def cmd_list(session, cmd, args, server):
    """LIST - List items available in the current shop (alias for ORDER)."""
    await cmd_order(session, cmd, args, server)


async def cmd_backroom(session, cmd, args, server):
    """BACKROOM [table] - Browse pawnshop backroom stock from the front room or inside the backroom."""
    shop, npc = await _get_shop_for_room(session, server)
    if not shop:
        return
    if not _is_pawn_shop(shop):
        await session.send_line("There is no pawnshop backroom here.")
        return
    await _cmd_pawn_backroom(session, server, shop, npc, args)


async def cmd_buy(session, cmd, args, server):
    """BUY <#|name> - Purchase an item from the shop."""
    if not args:
        await session.send_line("Buy what? Use ORDER to see available items, then BUY # or BUY <name>.")
        return

    shop, npc = await _get_shop_for_room(session, server)
    if not shop:
        return

    args_stripped = args.strip()
    lower_args = args_stripped.lower()
    if _is_pawn_shop(shop):
        if _is_pawn_backroom_room(shop, session.current_room.id):
            if await _cmd_buy_from_pawn_backroom(session, server, shop, npc, args_stripped, room_context_only=True):
                return
        if lower_args.startswith("backroom"):
            if await _cmd_buy_from_pawn_backroom(session, server, shop, npc, args_stripped):
                return

    items = _load_shop_inventory(server, shop["id"])
    if not items:
        await session.send_line(npc_speech(npc.name, f"says, 'I have nothing for sale right now.'"))
        return

    buy_mult = shop["buy_multiplier"]
    target_item = None

    # Try to match by number
    try:
        idx = int(args_stripped) - 1
        if 0 <= idx < len(items):
            target_item = items[idx]
    except ValueError:
        pass

    # Try to match by name
    if not target_item:
        search = args_stripped.lower()
        for item in items:
            if search in item["name"].lower() or search in item["short_name"].lower() or search in item["noun"].lower():
                target_item = item
                break

    if not target_item:
        await session.send_line(npc_speech(npc.name, f"says, 'I don't carry anything like that. Try ORDER to see my stock.'"))
        return

    # Check stock
    if target_item["stock"] == 0:
        await session.send_line(npc_speech(npc.name, f"says, 'I'm sold out of that, sorry.'"))
        return

    # Trading skill discount on buy price (Trading = ID 31, max 15% off)
    SKILL_TRADING = 31
    _tr_data = (getattr(session, 'skills', {}) or {}).get(SKILL_TRADING, {})
    _tr_ranks = int(_tr_data.get('ranks', 0)) if isinstance(_tr_data, dict) else 0
    trade_discount = min(0.15, _tr_ranks * 0.002)  # 0.2% per rank, cap 15%
    effective_mult = buy_mult * (1.0 - trade_discount)
    # Calculate price
    price = int(target_item["value"] * effective_mult)

    # Check funds
    if liquid_funds(session) < price:
        await session.send_line(
            npc_speech(
                npc.name,
                f"says, 'That costs {price} silver. You only have {liquid_funds_text(session)}. "
                "Come back when you can afford it.'"
            )
        )
        return

    # Check if player can hold the item after any note payment is resolved.
    hand_slot = receive_hand_after_payment(session, price)
    if not hand_slot:
        await session.send_line("Your hands are full! Free a hand first.")
        return

    # Add item to player inventory (in hand)
    inv_id = server.db.add_item_to_inventory(session.character_id, target_item["item_id"], slot=hand_slot)

    if inv_id:
        # Build item dict for session
        new_item = {
            "inv_id": inv_id,
            "item_id": target_item["item_id"],
            "name": target_item["name"],
            "short_name": target_item["short_name"],
            "noun": target_item["noun"],
            "article": target_item["article"],
            "item_type": target_item["item_type"],
            "value": target_item["value"],
            "weight": target_item["weight"],
            "slot": hand_slot,
        }
        # Load full item data
        conn = server.db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT i.*, ci.id as inv_id, ci.slot, ci.container_id, ci.quantity
                FROM character_inventory ci
                JOIN items i ON ci.item_id = i.id
                WHERE ci.id = %s
            """, (inv_id,))
            full_item = cur.fetchone()
            if full_item:
                new_item = full_item
                new_item["slot"] = hand_slot
        finally:
            conn.close()

        payment = spend_liquid_funds(session, server, price)
        if not payment.get("ok"):
            if inv_id:
                try:
                    server.db.remove_item_from_inventory(inv_id)
                except Exception:
                    pass
            await session.send_line("Something went wrong with the purchase.")
            return

        if hand_slot == "right_hand":
            session.right_hand = new_item
        else:
            session.left_hand = new_item

        # ── Toolkit population: fill with standard locksmith tools ────────
        if new_item.get("item_type") == "toolkit":
            await _populate_toolkit(session, server, new_item, hand_slot)

        # Decrement stock if limited
        if target_item["stock"] > 0:
            server.db.execute_query(
                "UPDATE shop_inventory SET stock = stock - 1 WHERE id = %s",
                (target_item["shop_inv_id"],)
            )

        # Save silver to DB
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver
        )

        await session.send_line(
            npc_speech(
                npc.name,
                f"{describe_payment(payment)} and hands you {colorize(target_item['name'], TextPresets.ITEM_NAME)}."
            )
        )

        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} just bought {target_item['name']}.",
            exclude=session
        )
    else:
        await session.send_line("Something went wrong with the purchase.")


import re as _re_shop
_ORDINAL_RE_SHOP = _re_shop.compile(r'^\d+(?:st|nd|rd|th)\s+', _re_shop.I)

def _item_matches(item, search):
    """Check if an item matches a search string using word-set matching.
    Strips ordinal prefix. All search words must appear in at least one
    name field, regardless of word order.
    e.g. 'midnight ora falchion' matches 'ora midnight falchion' ✓
    """
    s = _ORDINAL_RE_SHOP.sub('', search.lower()).strip()
    if not s:
        return False
    if item.get("is_order_slip") or (item.get("noun") or "").lower() == "order slip":
        return "order" in s or "slip" in s
    search_words = set(s.split())
    for field in ('short_name', 'name', 'noun'):
        val = (item.get(field) or '').lower()
        if not val:
            continue
        item_words = set(val.split())
        item_words.discard('a')
        item_words.discard('an')
        item_words.discard('the')
        item_words.discard('some')
        if search_words.issubset(item_words):
            return True
    return False


def _trade_sell_mult(session, base_mult):
    """Apply Trading skill bonus to sell multiplier (max +15%)."""
    SKILL_TRADING = 31
    d = (getattr(session, 'skills', {}) or {}).get(SKILL_TRADING, {})
    ranks = int(d.get('ranks', 0)) if isinstance(d, dict) else 0
    bonus = min(0.15, ranks * 0.002)
    return base_mult * (1.0 + bonus)


def _merge_extra_data(server, item, updates: dict):
    """
    Safely merge `updates` into an item's extra_data without clobbering
    existing fields (e.g. lock state on boxes).
    Reads current extra_data from DB, merges, writes back.
    """
    if not server.db or not item.get("inv_id"):
        return
    import json as _json
    inv_id = item["inv_id"]
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT extra_data FROM character_inventory WHERE id = %s", (inv_id,))
        row = cur.fetchone()
        existing = {}
        if row and row.get("extra_data"):
            try:
                existing = _json.loads(row["extra_data"]) if isinstance(row["extra_data"], str) else row["extra_data"]
            except Exception:
                existing = {}
        existing.update(updates)
        cur.execute("UPDATE character_inventory SET extra_data = %s WHERE id = %s",
                    (_json.dumps(existing), inv_id))
    except Exception as e:
        log.error("Failed to merge extra_data (inv_id=%s): %s", inv_id, e)
    finally:
        conn.close()
    # Also update the in-session dict so it's immediately reflected
    item.update(updates)


def _find_item_anywhere(session, search):
    """
    Find an item by search string in: right hand, left hand, worn inventory,
    and items inside worn containers.
    Returns (item_dict, location_string) or (None, None).
    Location string is 'right_hand', 'left_hand', 'worn', or 'in_container:<container_name>'.
    """
    if session.right_hand and _item_matches(session.right_hand, search):
        return session.right_hand, "right_hand"
    if session.left_hand and _item_matches(session.left_hand, search):
        return session.left_hand, "left_hand"
    for item in getattr(session, 'inventory', []):
        if item.get('slot') and item.get('slot') not in ('right_hand', 'left_hand') \
                and not item.get('container_id'):
            if _item_matches(item, search):
                return item, "worn"
    # Search inside all worn containers
    for item in getattr(session, 'inventory', []):
        if item.get('container_id'):
            if _item_matches(item, search):
                # Find the container name for a useful location string
                cont_id = item.get('container_id')
                cont_name = 'container'
                for c in getattr(session, 'inventory', []):
                    if c.get('inv_id') == cont_id:
                        cont_name = c.get('noun') or c.get('short_name') or 'container'
                        break
                return item, f"in_container:{cont_name}"
    return None, None


def _find_container_anywhere(session, search):
    """
    Find a container by search string in hands or worn slots.
    Returns item_dict or None.
    """
    for candidate in ([session.right_hand, session.left_hand] +
                      [i for i in getattr(session, 'inventory', [])
                       if i and i.get('item_type') == 'container'
                       and i.get('slot') and not i.get('container_id')]):
        if candidate and candidate.get('item_type') == 'container' and _item_matches(candidate, search):
            return candidate
    return None


async def cmd_sell(session, cmd, args, server):
    """
    SELL <item>           - Sell a single item held in your hand.
    SELL <container>      - If the container has contents, bulk sell them.
                            If the container is empty, sell the container itself.

    Bulk sell rules (applied to every item inside the container):
      - SKIP  items that are MARKED (protected by player)
      - SKIP  containers that are locked (even if unmarked)
      - SELL  everything else
    """
    if not args:
        await session.send_line("Sell what?  Hold an item in your hand, or specify a container to bulk-sell its contents.")
        return

    shop, npc = await _get_shop_for_room(session, server)
    if not shop:
        return

    search = args.strip()

    # ── Detect bulk sell: does the arg name a container? ──────────────────
    container = _find_container_anywhere(session, search)
    if container:
        cont_inv_id = container.get("inv_id")
        contents = [i for i in getattr(session, "inventory", [])
                    if i.get("container_id") == cont_inv_id]
        if contents:
            # Container has items — bulk sell the contents (existing behaviour)
            await _sell_container_contents(session, server, shop, npc, container)
            return
        # Container is empty — fall through to single-item sell so the
        # container itself gets sold (GS4 allows selling empty open containers)

    # ── Single item sell ───────────────────────────────────────────────────
    sell_item = None
    hand = None
    if session.right_hand and _item_matches(session.right_hand, search):
        sell_item, hand = session.right_hand, "right_hand"
    elif session.left_hand and _item_matches(session.left_hand, search):
        sell_item, hand = session.left_hand, "left_hand"

    if not sell_item:
        await session.send_line(
            f"You aren't holding anything like '{search}'.  "
            "You must have the item in your hand to sell it, or name a container to bulk-sell."
        )
        return

    if sell_item.get("is_order_slip") or (sell_item.get("noun") or "").lower() == "order slip":
        await session.send_line(
            colorize(
                "  Order slips cannot be sold.  Redeem it or drop it if you no longer need it.",
                TextPresets.WARNING
            )
        )
        return

    # Block selling marked items individually too — require explicit unmark first
    if sell_item.get("is_marked"):
        await session.send_line(
            colorize(
                f"  {sell_item.get('name', 'That item')} is marked and cannot be sold.  "
                "Use MARK REMOVE <item> to unmark it first.",
                TextPresets.WARNING
            )
        )
        return

    eff_mult = _trade_sell_mult(session, shop["sell_multiplier"])
    sell_price = max(1, int(sell_item.get("value", 0) * eff_mult))

    inv_id = sell_item.get("inv_id")
    if getattr(server, "guild", None):
        try:
            await server.guild.record_bounty_sale(session, shop, sell_item, npc)
        except Exception:
            pass
    if _is_pawn_shop(shop):
        _insert_item_into_pawn_backroom(server, shop, sell_item, session.character_name, session.character_id)
    if inv_id:
        server.db.remove_item_from_inventory(inv_id)
    setattr(session, hand, None)

    session.silver += sell_price
    server.db.save_character_resources(
        session.character_id,
        session.health_current, session.mana_current,
        session.spirit_current, session.stamina_current,
        session.silver
    )

    item_name = sell_item.get("name", "something")
    await session.send_line(
        npc_speech(npc.name,
            f"takes {colorize(item_name, TextPresets.ITEM_NAME)} from you and "
            f"hands you {colorize(str(sell_price) + ' silver', TextPresets.ITEM_NAME)}.")
    )
    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} just sold something to {npc.name}.",
        exclude=session
    )


async def _sell_container_contents(session, server, shop, npc, container):
    """Bulk sell all eligible items inside a container."""
    cont_inv_id = container.get("inv_id")
    cont_name   = container.get("short_name") or container.get("noun") or "container"
    contents    = [i for i in getattr(session, 'inventory', [])
                   if i.get("container_id") == cont_inv_id]

    if not contents:
        await session.send_line(
            npc_speech(npc.name, f"peers into your {cont_name}.  'There's nothing in there to sell.'")
        )
        return

    eff_mult    = _trade_sell_mult(session, shop["sell_multiplier"])
    total_silver = 0
    sold_lines   = []
    skipped_marked   = []
    skipped_locked   = []

    for item in contents:
        iname = item.get("name") or item.get("short_name") or "something"

        if item.get("is_order_slip") or (item.get("noun") or "").lower() == "order slip":
            continue

        # Rule 1: skip marked items
        if item.get("is_marked"):
            skipped_marked.append(iname)
            continue

        # Rule 2: skip locked containers
        if item.get("item_type") == "container" and item.get("is_locked"):
            skipped_locked.append(iname)
            continue

        # Sell it
        price = max(1, int((item.get("value") or 0) * eff_mult))
        inv_id = item.get("inv_id")
        if getattr(server, "guild", None):
            try:
                await server.guild.record_bounty_sale(session, shop, item, npc)
            except Exception:
                pass
        if _is_pawn_shop(shop):
            _insert_item_into_pawn_backroom(server, shop, item, session.character_name, session.character_id)
        if inv_id:
            server.db.remove_item_from_inventory(inv_id)
            session.inventory = [i for i in session.inventory if i.get("inv_id") != inv_id]
        total_silver += price
        sold_lines.append(f"  {colorize(iname, TextPresets.ITEM_NAME)} — {price} silver")

    if not sold_lines:
        await session.send_line(
            npc_speech(npc.name,
                f"looks through your {cont_name} but everything is either marked or locked.")
        )
        if skipped_marked:
            await session.send_line(colorize(
                f"  Marked (skipped): {', '.join(skipped_marked)}", TextPresets.SYSTEM))
        if skipped_locked:
            await session.send_line(colorize(
                f"  Locked containers (skipped): {', '.join(skipped_locked)}", TextPresets.SYSTEM))
        return

    # Pay out
    session.silver += total_silver
    server.db.save_character_resources(
        session.character_id,
        session.health_current, session.mana_current,
        session.spirit_current, session.stamina_current,
        session.silver
    )

    await session.send_line(
        npc_speech(npc.name, f"goes through your {cont_name} and buys the following:")
    )
    for line in sold_lines:
        await session.send_line(line)
    await session.send_line(
        colorize(f"  Total received: {total_silver} silver.", TextPresets.ITEM_NAME)
    )

    if skipped_marked:
        await session.send_line(colorize(
            f"  Marked (skipped): {', '.join(skipped_marked)}", TextPresets.SYSTEM))
    if skipped_locked:
        await session.send_line(colorize(
            f"  Locked containers (skipped): {', '.join(skipped_locked)}", TextPresets.SYSTEM))

    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} sells a pile of goods to {npc.name}.",
        exclude=session
    )


# =========================================================
# MARK
# =========================================================

async def cmd_mark(session, cmd, args, server):
    """
    MARK              - List all your currently marked items.
    MARK <item>       - Mark an item (protects it from bulk selling / trash).
    MARK REMOVE <item>- Remove the mark from an item.

    Marked items are skipped by SELL <container> and cannot be accidentally
    sold or trashed.  The mark persists across logout/login.
    Items can be in your hands or worn/carried in your inventory.
    """
    args_str = (args or "").strip()

    # ── MARK with no args: list marked items ──────────────────────────────
    if not args_str:
        all_items = (
            ([session.right_hand] if session.right_hand else []) +
            ([session.left_hand]  if session.left_hand  else []) +
            list(getattr(session, 'inventory', []))
        )
        marked = [i for i in all_items if i and i.get("is_marked")]
        if not marked:
            await session.send_line("You have no marked items.")
            await session.send_line(colorize(
                "  Use MARK <item> to protect an item from bulk selling.",
                TextPresets.SYSTEM))
            return
        await session.send_line(colorize("Marked items (protected from bulk selling):", TextPresets.SYSTEM))
        for item in marked:
            if item is session.right_hand:
                loc = "right hand"
            elif item is session.left_hand:
                loc = "left hand"
            elif item.get('container_id'):
                # Find the container name
                cont_id = item.get('container_id')
                cont_name = 'a container'
                for c in getattr(session, 'inventory', []):
                    if c.get('inv_id') == cont_id:
                        cont_name = c.get('noun') or c.get('short_name') or 'a container'
                        break
                loc = f"in your {cont_name}"
            else:
                loc = item.get("slot", "inventory")
            await session.send_line(
                f"  {colorize(item.get('name', 'unknown'), TextPresets.ITEM_NAME)}"
                f"  [{loc}]"
            )
        return

    # ── MARK REMOVE <item> ────────────────────────────────────────────────
    remove_mode = False
    if args_str.lower().startswith("remove "):
        remove_mode = True
        args_str = args_str[7:].strip()

    if not args_str:
        await session.send_line("Mark or unmark which item?")
        return

    item, location = _find_item_anywhere(session, args_str)

    if not item:
        await session.send_line(
            f"You don't see '{args_str}' on you.  "
            "The item must be in your hands, worn, or inside a worn container."
        )
        return

    iname = item.get("name") or item.get("short_name") or "that item"

    if remove_mode:
        if not item.get("is_marked"):
            await session.send_line(
                colorize(f"  {iname} is not marked.", TextPresets.SYSTEM)
            )
            return
        _merge_extra_data(server, item, {"is_marked": False})
        await session.send_line(
            colorize(f"  You remove the mark from {colorize(iname, TextPresets.ITEM_NAME)}.", TextPresets.SYSTEM)
        )
    else:
        if item.get("is_marked"):
            await session.send_line(
                colorize(f"  {iname} is already marked.", TextPresets.SYSTEM)
            )
            return
        _merge_extra_data(server, item, {"is_marked": True})
        await session.send_line(
            colorize(
                f"  You mark {colorize(iname, TextPresets.ITEM_NAME)}.  "
                "It will be skipped during bulk selling.",
                TextPresets.SYSTEM
            )
        )


async def cmd_appraise(session, cmd, args, server):
    """APPRAISE <item> - Get the sell value of an item in your hands."""
    if not args:
        await session.send_line("Appraise what? Hold the item in your hand first.")
        return

    from server.core.commands.player.boxpick import maybe_handle_locksmith_appraise

    if await maybe_handle_locksmith_appraise(session, args, server):
        return

    shop, npc = await _get_shop_for_room(session, server)
    if not shop:
        return

    sell_mult = shop["sell_multiplier"]
    search = args.strip().lower()

    # Find item in hands
    appraise_item = None
    if session.right_hand:
        rh = session.right_hand
        if (search in rh.get("name", "").lower() or
            search in rh.get("short_name", "").lower() or
            search in rh.get("noun", "").lower()):
            appraise_item = rh
    if not appraise_item and session.left_hand:
        lh = session.left_hand
        if (search in lh.get("name", "").lower() or
            search in lh.get("short_name", "").lower() or
            search in lh.get("noun", "").lower()):
            appraise_item = lh

    if not appraise_item:
        await session.send_line(f"You aren't holding anything like '{args.strip()}'.")
        return

    base_value = appraise_item.get("value", 0)
    sell_price = max(1, int(base_value * sell_mult))
    item_name = appraise_item.get("name", "that")

    await session.send_line(
        npc_speech(npc.name, f"examines {colorize(item_name, TextPresets.ITEM_NAME)} carefully.")
    )
    await session.send_line(
        npc_speech(npc.name, f'says, "I\'d give you {colorize(str(sell_price) + " silver", TextPresets.ITEM_NAME)} for that."')
    )


async def cmd_ask_npc(session, cmd, args, server):
    """ASK <npc> ABOUT <topic> - Talk to an NPC."""
    if not args:
        await session.send_line("Ask whom about what?")
        return

    npc_name, topic = _parse_npc_topic(args, require_topic=True)
    if not npc_name or topic is None:
        await session.send_line("Ask whom about what? Try: ASK <person> ABOUT <topic>")
        return

    if not hasattr(server, 'npcs'):
        await session.send_line("There's nobody here to ask.")
        return

    npc = server.npcs.find_npc_in_room(session.current_room.id, npc_name)
    if not npc:
        await session.send_line(f"You don't see '{npc_name}' here.")
        return

    await _send_npc_response(session, npc, topic, server)


async def cmd_talk_npc(session, cmd, args, server):
    """TALK [TO] <npc> [ABOUT <topic>] - Natural NPC conversation entrypoint."""
    if not args:
        await session.send_line("Talk to whom?")
        return

    npc_name, topic = _parse_npc_topic(args, require_topic=False)
    if not npc_name:
        await session.send_line("Talk to whom?")
        return

    if not hasattr(server, "npcs"):
        await session.send_line("There's nobody here to talk to.")
        return

    npc = server.npcs.find_npc_in_room(session.current_room.id, npc_name)
    if not npc:
        await session.send_line(f"You don't see '{npc_name}' here.")
        return

    await _send_npc_response(session, npc, topic, server)

# ── Toolkit auto-population ──────────────────────────────────────────────────
# When a player buys a toolkit, it comes pre-loaded with the 6 standard tools.
# Consumable tools (putty, cotton, acid vials) start with 100 charges.

_TOOLKIT_CONTENTS = [
    # (noun_to_match, charges_or_None)
    ("putty",   100),    # consumable
    ("cotton",  100),    # consumable
    ("vials",   100),    # consumable (acid vials)
    ("grips",   None),   # permanent
    ("file",    None),   # permanent
    ("needle",  None),   # permanent
]


async def _populate_toolkit(session, server, toolkit_item: dict, hand_slot: str):
    """Fill a newly-purchased toolkit with its 6 standard tools.
    Each tool is loaded from the items table by noun + item_type match,
    then added as contents of the toolkit container."""
    contents = []
    db = server.db
    conn = db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        for noun, charges in _TOOLKIT_CONTENTS:
            cur.execute("""
                SELECT id, name, short_name, noun, item_type, value, description
                FROM items
                WHERE noun = %s AND item_type IN ('disarm_tool', 'disarm_supply')
                  AND is_template = 1
                LIMIT 1
            """, (noun,))
            row = cur.fetchone()
            if row:
                tool = {
                    "item_id":    row["id"],
                    "name":       row["name"],
                    "short_name": row["short_name"],
                    "noun":       row["noun"],
                    "item_type":  row["item_type"],
                    "value":      row["value"],
                }
                if charges is not None:
                    tool["charges"] = charges
                contents.append(tool)
    finally:
        conn.close()

    toolkit_item["contents"] = contents

    # Persist contents to DB via extra_data
    inv_id = toolkit_item.get("inv_id")
    if inv_id and db:
        db.save_item_extra_data(inv_id, {
            "contents": contents,
        })

    # Update the hand slot reference
    if hand_slot == "right_hand":
        session.right_hand = toolkit_item
    else:
        session.left_hand = toolkit_item
