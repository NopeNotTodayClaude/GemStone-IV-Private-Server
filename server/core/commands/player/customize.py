"""
customize.py  -  Custom order system for GemStone IV shops.

COMPLETE REWRITE.  The old flow was broken.  This replaces it entirely.

PLAYER-FACING FLOW
==================
  Step 1  ORDER                    browse catalog
  Step 2  CUSTOMIZE                show material/color menu for selected item
          CUSTOMIZE 3              pick material #3
          CUSTOMIZE 3 silver       material #3 + color silver in one step
          CUSTOMIZE vultite        pick material by name
          CUSTOMIZE vultite red    material by name + color
  Step 3  CONFIRM                  NPC quotes final price, shows summary
          CONFIRM YES              pay silver, receive order slip in hand
          CONFIRM NO               cancel
  Step 4  (timer: 0-60 sec)       server announces "Your order is ready!"
  Step 5  REDEEM                   at same shop, holding slip -> receive item
"""

import asyncio
import logging
import json as _json
from server.core.protocol.colors import colorize, TextPresets, npc_speech
from server.core.commands.player.currency import (
    liquid_funds,
    liquid_funds_text,
    receive_hand_after_payment,
    spend_liquid_funds,
    describe_payment,
)
from server.core.world.material_data import (
    COLORS, get_material, get_materials_for_item_type,
    can_use_material, apply_material_to_item, apply_color_to_item,
    is_clothing_item,
)

log = logging.getLogger(__name__)

_DEFAULT_WAIT_CFG = {
    "min_seconds": 0,
    "max_seconds": 60,
    "no_material_seconds": 0,
    "default_material_seconds": 10,
    "instant_materials": {
        "iron": True,
        "steel": True,
        "bronze": True,
    },
    "material_seconds": {
        "silver": 5,
        "gold": 5,
        "invar": 10,
        "mithril": 15,
        "ora": 20,
        "imflass": 25,
        "laje": 28,
        "carmiln": 30,
        "faenor": 34,
        "gornar": 36,
        "rhimar": 38,
        "zorchar": 40,
        "drakar": 42,
        "razern": 44,
        "vaalorn": 46,
        "glaes": 48,
        "mithglin": 50,
        "veniom": 50,
        "eahnor": 52,
        "vultite": 54,
        "rolaren": 55,
        "eonake": 56,
        "kelyn": 57,
        "urglaes": 58,
        "golvern": 59,
        "krodera": 60,
        "kroderine": 60,
        "coraesine": 60,
    },
}


def _get_wait_cfg(server) -> dict:
    lua_mgr = getattr(server, "lua", None)
    try:
        if lua_mgr:
            cfg = lua_mgr.get_customize_cfg() or {}
            order_wait = cfg.get("order_wait", {})
            if isinstance(order_wait, dict):
                return order_wait
    except Exception as e:
        log.warning("customize: failed to load Lua wait config (%s)", e)
    return _DEFAULT_WAIT_CFG


def _clamp_wait(seconds: int, cfg: dict) -> int:
    minimum = max(0, int(cfg.get("min_seconds", 0)))
    maximum = max(minimum, int(cfg.get("max_seconds", 60)))
    return max(minimum, min(maximum, int(seconds)))


def _order_time(server, pending: dict) -> int:
    cfg = _get_wait_cfg(server)
    material = str((pending or {}).get("material") or "").strip().lower()
    if not material:
        return _clamp_wait(int(cfg.get("no_material_seconds", 0)), cfg)

    instant = cfg.get("instant_materials", {})
    if isinstance(instant, dict) and instant.get(material):
        return _clamp_wait(0, cfg)

    material_seconds = cfg.get("material_seconds", {})
    if isinstance(material_seconds, dict) and material in material_seconds:
        return _clamp_wait(int(material_seconds.get(material, 0)), cfg)

    return _clamp_wait(int(cfg.get("default_material_seconds", 10)), cfg)


def _format_wait(seconds: int) -> str:
    seconds = max(0, int(seconds))
    if seconds <= 0:
        return "immediately"
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    minutes, rem = divmod(seconds, 60)
    minute_text = f"{minutes} minute{'s' if minutes != 1 else ''}"
    if rem <= 0:
        return minute_text
    return f"{minute_text} {rem} second{'s' if rem != 1 else ''}"


def _fmt_rarity(rarity):
    return {
        "common": "Common", "infrequent": "Infrequent",
        "uncommon": "Uncommon", "rare": "Rare",
        "very_rare": "Very Rare", "extremely_rare": "Extremely Rare",
    }.get(rarity, rarity.title())


def _ensure_lists(session):
    if not hasattr(session, "_active_orders") or session._active_orders is None:
        session._active_orders = []
    if not hasattr(session, "_ready_orders") or session._ready_orders is None:
        session._ready_orders = []


def _get_pending(session):
    return getattr(session, "_pending_order", None)


def _clear_pending(session):
    session._pending_order       = None
    session._customize_materials = None
    session._confirm_pending     = False


def _build_summary(pending):
    item     = pending["item"]
    price    = pending.get("price", item.get("value", 0))
    material = pending.get("material")
    color    = pending.get("color")
    name     = item.get("name", "an item")
    mods     = []
    if material:
        mat = get_material(material)
        if mat:
            b = mat.get("enchant_bonus", 0)
            mods.append(mat["display"] + (f" +{b}" if b else ""))
    if color:
        mods.append(f"{color} color")
    mod_str = f"  [{', '.join(mods)}]" if mods else ""
    return (
        f"{colorize(name, TextPresets.ITEM_NAME)}"
        f"{colorize(mod_str, TextPresets.SYSTEM)}"
        f"  — {colorize(str(price) + ' silver', TextPresets.ITEM_NAME)}"
    )


# ── CUSTOMIZE ────────────────────────────────────────────────────────────────

async def cmd_customize(session, cmd, args, server):
    args = (args or "").strip()

    pending = _get_pending(session)
    if not pending:
        await session.send_line(
            "You need to ORDER an item first.  Type ORDER to see the catalog."
        )
        return

    item = pending.get("item")
    if not item:
        await session.send_line("No item is currently selected.")
        return

    if not args:
        if is_clothing_item(item):
            await _show_color_menu(session, item)
        else:
            await _show_customize_menu(session, item)
        return

    parts   = args.split(None, 1)
    mat_arg = parts[0]
    col_arg = parts[1].strip().lower() if len(parts) > 1 else None

    # Clothing: color-only — treat the entire arg as a color
    if is_clothing_item(item):
        color = mat_arg.lower()
        if color not in COLORS:
            await session.send_line(
                f"'{color}' is not an available color.  Type CUSTOMIZE to see the color list."
            )
            return
        await _apply_color_choice(session, item, color)
        return

    materials = getattr(session, "_customize_materials", None)
    if not materials:
        materials = get_materials_for_item_type(item.get("item_type", "misc"))
        session._customize_materials = materials

    # Resolve material
    selected_key = None
    try:
        idx = int(mat_arg) - 1
        if 0 <= idx < len(materials):
            selected_key = materials[idx]["key"]
        else:
            await session.send_line(f"Choose a number between 1 and {len(materials)}.")
            return
    except ValueError:
        mat = get_material(mat_arg)
        if mat:
            selected_key = mat_arg.lower().strip()
        else:
            await session.send_line(
                f"'{mat_arg}' is not a recognized material.  Type CUSTOMIZE to see options."
            )
            return

    ok, reason = can_use_material(session.level, selected_key)
    if not ok:
        await session.send_line(reason)
        return

    mat     = get_material(selected_key)
    updated = apply_material_to_item(item, selected_key)
    pending["material"] = selected_key
    pending["item"]     = updated

    bonus_str = f"+{mat['enchant_bonus']}" if mat.get("enchant_bonus", 0) > 0 else "no enchantment"

    # Optional color
    col_note = ""
    if col_arg:
        if col_arg not in COLORS:
            col_note = (
                f"\n  Note: '{col_arg}' is not a recognized color.  Material applied, color skipped."
            )
        else:
            updated = apply_color_to_item(updated, col_arg)
            pending["color"] = col_arg
            pending["item"]  = updated
            col_note = f"  Color: {col_arg}."

    # Recalculate price
    buy_mult       = pending.get("shop", {}).get("buy_multiplier", 1.0)
    quantity       = pending.get("quantity", 1)
    pending["price"] = int(updated.get("value", 0) * buy_mult) * quantity

    await session.send_line(
        colorize(
            f"Material set to {mat['display']} ({bonus_str}).{col_note}\n"
            f"New price: {pending['price']:,} silver.\n"
            f"Type CONFIRM to review and place your order.",
            TextPresets.ITEM_NAME
        )
    )
    session._confirm_pending = False


async def _show_customize_menu(session, item):
    itype     = item.get("item_type", "misc")
    materials = get_materials_for_item_type(itype)
    session._customize_materials = materials

    # Inject hidden tag for HUD to make materials clickable
    mat_payload = []
    for idx, mat in enumerate(materials, 1):
        mat_payload.append({
            "idx": idx,
            "key": mat["key"],
            "display": mat["display"],
            "enchant_bonus": mat.get("enchant_bonus", 0),
            "attack_mod": mat.get("attack_mod", 0),
            "defense_mod": mat.get("defense_mod", 0),
            "weight_modifier": mat.get("weight_modifier", 1.0),
            "cost_mult": mat.get("cost_mult", 1.0),
            "rarity": mat.get("rarity", "common"),
            "level_req": mat.get("level_req", 0),
            "special": mat.get("special", ""),
            "description": mat.get("description", ""),
            "can_use": session.level >= mat.get("level_req", 0),
        })
    await session.send_line(
        f"\x00CUSTOMIZE_MENU:{_json.dumps({'item_name': item.get('name',''), 'item_type': itype, 'materials': mat_payload, 'colors': COLORS})}\x00"
    )

    lines = [
        colorize(f"[Customization options for: {item.get('name','this item')}]", TextPresets.ITEM_NAME),
        colorize(f"  {'#':<4} {'Material':<14} {'Bonus':<8} {'Level':<8} Rarity", TextPresets.SYSTEM),
        colorize("  " + "-" * 60, TextPresets.SYSTEM),
    ]
    for idx, mat in enumerate(materials, 1):
        lvl   = mat.get("level_req", 0)
        bonus = mat.get("enchant_bonus", 0)
        can   = session.level >= lvl
        clr   = TextPresets.ITEM_NAME if can else TextPresets.COMBAT_MISS
        line  = (
            f"  {idx:<4} {mat['display']:<14} "
            f"{('+'+str(bonus)) if bonus else '—':<8} "
            f"{'Lv '+str(lvl) if lvl else 'Any':<8} "
            f"{_fmt_rarity(mat.get('rarity',''))}"
        )
        lines.append(colorize(line, clr))

    lines += [
        colorize("  " + "-" * 60, TextPresets.SYSTEM),
        colorize(f"  Colors: {', '.join(COLORS[:18])}...", TextPresets.SYSTEM),
        colorize("  CUSTOMIZE #           — pick material by number", TextPresets.SYSTEM),
        colorize("  CUSTOMIZE # <color>   — material + color together", TextPresets.SYSTEM),
        colorize("  Grey = level requirement not met.", TextPresets.COMBAT_MISS),
    ]
    await session.send_line("\r\n".join(lines))


async def _show_color_menu(session, item):
    """Color-only CUSTOMIZE menu for clothing items."""
    # Inject hidden tag for HUD to make colors clickable
    await session.send_line(
        f"\x00CUSTOMIZE_COLORS:{_json.dumps({'item_name': item.get('name',''), 'colors': COLORS})}\x00"
    )

    lines = [
        colorize(f"[Color options for: {item.get('name', 'this item')}]", TextPresets.ITEM_NAME),
        colorize("  Type CUSTOMIZE <color name> to apply a color.", TextPresets.SYSTEM),
        colorize("  " + "-" * 60, TextPresets.SYSTEM),
    ]
    row = []
    for color in COLORS:
        row.append(f"{color:<12}")
        if len(row) == 6:
            lines.append("  " + "".join(row))
            row = []
    if row:
        lines.append("  " + "".join(row))
    lines.append(colorize("  " + "-" * 60, TextPresets.SYSTEM))
    lines.append(colorize("  Example:  CUSTOMIZE crimson", TextPresets.SYSTEM))
    await session.send_line("\r\n".join(lines))


async def _apply_color_choice(session, item, color):
    """Apply color to a clothing item and update the pending order."""
    updated = apply_color_to_item(item, color)
    session._pending_order["color"] = color
    session._pending_order["item"]  = updated
    buy_mult = session._pending_order.get("shop", {}).get("buy_multiplier", 1.0)
    quantity = session._pending_order.get("quantity", 1)
    session._pending_order["price"] = int(updated.get("value", 0) * buy_mult) * quantity
    await session.send_line(
        colorize(
            f"Color set to {color}.  New price: {session._pending_order['price']:,} silver.\n"
            f"Type CONFIRM to review and place your order.",
            TextPresets.ITEM_NAME
        )
    )


# ── CONFIRM ──────────────────────────────────────────────────────────────────

async def cmd_confirm(session, cmd, args, server):
    args = (args or "").strip().upper()
    _ensure_lists(session)

    pending = _get_pending(session)
    if not pending:
        await session.send_line(
            "You don't have a pending order.  Use ORDER to browse the catalog."
        )
        return

    shop = pending.get("shop")
    npc  = pending.get("npc")
    item = pending.get("item")
    if not shop or not npc or not item:
        await session.send_line("Something went wrong.  Please ORDER the item again.")
        _clear_pending(session)
        return

    if args == "YES":
        price = pending.get("price", item.get("value", 0))

        if liquid_funds(session) < price:
            await session.send_line(
                npc_speech(
                    npc.name,
                    f"says, 'That'll be {price:,} silver - you only have {liquid_funds_text(session)}.  "
                    "Come back when you have the coin.'"
                )
            )
            return
            await session.send_line(
                npc_speech(npc.name,
                    f"says, 'That'll be {price:,} silver — you only have {session.silver:,}.  "
                    "Come back when you have the coin.'")
            )
            return

        slip_hand = receive_hand_after_payment(session, price)
        if not slip_hand:
            await session.send_line("Your hands are full.  Free a hand to receive the order slip.")
            return

        order_secs   = _order_time(server, pending)
        order_record = {
            "item":        item,
            "shop_id":     shop["id"],
            "shop_name":   shop["name"],
            "npc_name":    npc.name,
            "room_id":     shop.get("room_id"),
            "price_paid":  price,
            "ready":       False,
            "slip_inv_id": None,
        }

        slip = _give_order_slip(session, server, item, shop, hand=slip_hand, assign=False)
        if not slip:
            await session.send_line("The clerk frowns and cannot prepare your order slip right now.")
            return

        payment = spend_liquid_funds(session, server, price)
        if not payment.get("ok"):
            if slip.get("inv_id"):
                try:
                    server.db.remove_item_from_inventory(slip["inv_id"])
                except Exception:
                    pass
            await session.send_line("Something went wrong while processing the payment.")
            return

        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver
        )

        if slip_hand == "right_hand":
            session.right_hand = slip
        else:
            session.left_hand = slip

        order_record["slip_inv_id"] = slip.get("inv_id")
        session._active_orders.append(order_record)

        asyncio.ensure_future(
            _order_completion_task(session, server, order_record, order_secs)
        )

        mat_note = ""
        if pending.get("material"):
            mat = get_material(pending["material"])
            if mat:
                mat_note = f" in {mat['display']}"
        col_note = f", {pending['color']} color" if pending.get("color") else ""
        wait_str = _format_wait(order_secs)

        if order_secs <= 0:
            ready_phrase = (
                f"'Your {item.get('noun','item')}{mat_note}{col_note} is ready right away.  "
                "You can REDEEM your slip immediately.'"
            )
        else:
            ready_phrase = (
                f"'Your {item.get('noun','item')}{mat_note}{col_note} will be ready "
                f"in about {wait_str}.  Return here and REDEEM your slip when it's done.'"
            )

        await session.send_line(
            npc_speech(npc.name,
                f"{describe_payment(payment)} and passes you an order slip.  {ready_phrase}"
            )
        )
        await session.send_line(
            colorize(f"  [Order slip placed in your {slip_hand.replace('_',' ')}.]\n", TextPresets.SYSTEM)
        )
        _clear_pending(session)
        return

    if args == "NO":
        await session.send_line(
            npc_speech(npc.name, "says, 'No problem.  Let me know if you change your mind.'")
        )
        _clear_pending(session)
        return

    # No arg — show summary
    price = pending.get("price", item.get("value", 0))
    order_secs = _order_time(server, pending)

    await session.send_line(npc_speech(npc.name, "looks over your selections."))
    await session.send_line(colorize("\n  \u2500\u2500 Order Summary \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500", TextPresets.SYSTEM))
    await session.send_line(f"  Item   : {_build_summary(pending)}")

    # ── Item stat preview (Fix 2A) ──────────────────────────────────────
    try:
        from server.core.commands.player.inventory import _item_stat_lines
        for stat_line in _item_stat_lines(item):
            await session.send_line(stat_line)
    except Exception:
        pass
    # ────────────────────────────────────────────────────────────────────

    await session.send_line(colorize(f"  Total  : {price:,} silver  (you have {session.silver:,})", TextPresets.ITEM_NAME))
    if order_secs <= 0:
        ready_line = "  Ready  : immediately after payment"
    else:
        ready_line = f"  Ready  : about {_format_wait(order_secs)} after payment"
    await session.send_line(colorize(ready_line, TextPresets.SYSTEM))
    await session.send_line(colorize("  " + "\u2500" * 44, TextPresets.SYSTEM))
    await session.send_line(colorize("  Type CONFIRM YES to pay and place the order, or CONFIRM NO to cancel.", TextPresets.ITEM_NAME))
    session._confirm_pending = True


# ── REDEEM ───────────────────────────────────────────────────────────────────

async def cmd_redeem(session, cmd, args, server):
    _ensure_lists(session)

    slip = _find_slip_in_hands(session)
    if not slip:
        await session.send_line(
            "You need to hold your order slip.  Check INVENTORY if you can't find it."
        )
        return

    slip_inv_id = slip.get("inv_id")

    ready = next((o for o in session._ready_orders if o.get("slip_inv_id") == slip_inv_id), None)
    if not ready:
        active = next((o for o in session._active_orders if o.get("slip_inv_id") == slip_inv_id), None)
        if active:
            await session.send_line("Your order isn't ready yet.  You'll be notified when it is.")
        else:
            await session.send_line("That slip doesn't match any of your outstanding orders.")
        return

    npc = server.npcs.get_shopkeeper_in_room(session.current_room.id) if hasattr(server, "npcs") else None
    if not npc or not npc.shop_id:
        await session.send_line("There is no shopkeeper here to redeem with.")
        return

    if ready.get("shop_id") != npc.shop_id:
        await session.send_line(
            npc_speech(npc.name, "says, 'That slip isn't from my shop.  You'll need to return to where you placed your order.'")
        )
        return

    if session.right_hand and session.left_hand:
        await session.send_line("Your hands are full.  Free a hand to receive your item.")
        return

    # Remove slip
    if slip_inv_id:
        server.db.remove_item_from_inventory(slip_inv_id)
    hand = "right_hand" if not session.right_hand else "left_hand"
    if session.right_hand is slip:
        session.right_hand = None
    elif session.left_hand is slip:
        session.left_hand = None
    session.inventory = [i for i in getattr(session, "inventory", []) if i.get("inv_id") != slip_inv_id]

    # Deliver item
    finished = ready["item"]
    _deliver_item(session, server, finished, hand)
    session._ready_orders = [o for o in session._ready_orders if o.get("slip_inv_id") != slip_inv_id]

    name = finished.get("name", "your item")
    await session.send_line(
        npc_speech(npc.name, f"takes your slip and presents you with {colorize(name, TextPresets.ITEM_NAME)}.")
    )
    await session.send_line(colorize(f"  [{name} placed in your {hand.replace('_',' ')}.]\n", TextPresets.SYSTEM))
    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} redeems an order and receives {name}.",
        exclude=session
    )


# ── Internal helpers ─────────────────────────────────────────────────────────

def _give_order_slip(session, server, item, shop, hand=None, assign=True):
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM items WHERE noun = 'order slip' AND is_template = TRUE LIMIT 1")
        row = cur.fetchone()
        if row:
            base_id = row[0]
        else:
            cur.execute("""
                INSERT INTO items
                    (name, short_name, base_name, noun, article,
                     item_type, material, weight, value, description, is_template)
                VALUES
                    ('an order slip','order slip','order slip','order slip','an',
                     'misc','paper',0.1,0,'A slip detailing a custom order.',TRUE)
            """)
            base_id = cur.lastrowid
        conn.commit()
    except Exception as e:
        log.error("order slip template error: %s", e)
        return None
    finally:
        conn.close()

    hand = hand or ("right_hand" if not session.right_hand else "left_hand")
    inv_id = server.db.add_item_to_inventory(session.character_id, base_id, slot=hand)
    if not inv_id:
        return None

    server.db.save_item_extra_data(inv_id, {
        "is_order_slip": True,
        "order_item":    item.get("name", ""),
        "shop_id":       shop["id"],
        "ready":         False,
    })

    slip = {
        "inv_id": inv_id, "item_id": base_id,
        "name": f"an order slip for {item.get('name','an item')}",
        "short_name": "order slip", "noun": "order slip",
        "article": "an", "item_type": "misc",
        "value": 0, "weight": 0.1, "slot": hand,
        "is_order_slip": True, "shop_id": shop["id"],
    }
    if assign:
        if hand == "right_hand":
            session.right_hand = slip
        else:
            session.left_hand = slip

    return slip


def _deliver_item(session, server, item, hand):
    item_id = item.get("item_id") or item.get("id")
    if not item_id:
        return None
    inv_id = server.db.add_item_to_inventory(session.character_id, item_id, slot=hand)
    if not inv_id:
        return None
    extra = {}
    for k in ("material", "color", "enchant_bonus"):
        if item.get(k):
            extra[k] = item[k]
    if item.get("name"):
        extra["custom_name"] = item["name"]
    if extra:
        server.db.save_item_extra_data(inv_id, extra)
    item["inv_id"] = inv_id
    item["slot"]   = hand
    setattr(session, hand, item)
    return inv_id


def _find_slip_in_hands(session):
    for item in [session.right_hand, session.left_hand]:
        if item and (item.get("is_order_slip") or item.get("noun") == "order slip"):
            return item
    return None


async def _order_completion_task(session, server, order_record, delay):
    await asyncio.sleep(delay)
    if order_record in session._active_orders:
        session._active_orders.remove(order_record)
    order_record["ready"] = True
    session._ready_orders.append(order_record)
    slip_id = order_record.get("slip_inv_id")
    if slip_id:
        try:
            server.db.save_item_extra_data(slip_id, {"is_order_slip": True, "ready": True})
        except Exception as e:
            log.warning("slip extra_data update failed: %s", e)
    name  = order_record["item"].get("name", "your order")
    shop  = order_record.get("shop_name", "the shop")
    await session.send_line(
        colorize(
            f"\n  [Your order of {name} from {shop} is ready!  "
            "Return and type REDEEM while holding your slip.]\n",
            TextPresets.ITEM_NAME
        )
    )
