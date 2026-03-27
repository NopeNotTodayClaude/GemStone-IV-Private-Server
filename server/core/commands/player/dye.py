"""
dye.py
------
DYE command handler.

Usage:
  DYE <item> <color>       -- dye a worn/held item (overwrites existing color)
  DYE <item> REMOVE        -- strip dye, restore to natural color
  DYE HAIR <color>         -- dye your hair
  DYE HAIR REMOVE          -- restore natural hair color

Rules:
  - Player must have an appropriate dye vial in inventory (item_type='dye',
    color field matches the requested color).
  - One vial is consumed per use (removed from inventory).
  - Works on any wearable item (worn_location is not null) and on hair.
  - Color change is stored in character_inventory.color (via extra_data) for
    items, and in session.hair_color for hair.
  - REMOVE is always free (no vial needed).
"""

import logging
from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)

# ── Canonical color list ──────────────────────────────────────────────────────
# All GS4 standard dye colors + custom server additions.
# Used for validation and to help the player pick a name.
VALID_COLORS = [
    # Whites / Greys / Blacks
    "white", "ivory", "cream", "eggshell", "ash", "silver", "grey", "charcoal", "black",
    # Reds
    "red", "crimson", "scarlet", "burgundy", "maroon", "ruby", "rose", "pink",
    # Oranges
    "orange", "amber", "copper", "rust", "coral",
    # Yellows
    "yellow", "gold", "golden", "saffron", "ochre",
    # Greens
    "green", "lime", "olive", "forest", "jade", "emerald", "sage", "moss",
    # Blues
    "blue", "cobalt", "navy", "sapphire", "azure", "cerulean", "teal",
    "periwinkle", "indigo",
    # Purples
    "purple", "violet", "lavender", "plum", "mauve",
    # Browns / Tans
    "brown", "tan", "tawny", "umber", "sienna", "mahogany", "chestnut",
    # Special / Custom
    "ambrosia",   # soft golden honey-hue
    "rainbow",    # festival / special
    "ebony",
    "onyx",
    "snow",
    "midnight",
    "shadow",
    "smoke",
    "sand",
    "loden",
    "slate",
]

# Normalise any alias the player might type
_COLOR_ALIASES = {
    "gray":         "grey",
    "gray-blue":    "slate",
    "gray-green":   "sage",
    "dark red":     "crimson",
    "dark blue":    "navy",
    "light blue":   "cerulean",
    "sky blue":     "azure",
    "hot pink":     "rose",
    "bright pink":  "pink",
    "dark purple":  "plum",
    "light purple": "lavender",
    "dark green":   "forest",
    "light green":  "lime",
    "bright red":   "scarlet",
    "bright yellow":"gold",
}


def _normalize_color(raw: str) -> str:
    """Lower-case, strip, resolve alias."""
    c = raw.strip().lower()
    return _COLOR_ALIASES.get(c, c)


def _find_dye_vial(session, color: str):
    """Return the first dye vial (item_type='dye') matching color.
    Searches right hand, left hand, then full inventory (including containers).
    """
    color_l = color.strip().lower()

    def _matches(item):
        if not item:
            return False
        if item.get("item_type") != "dye":
            return False
        return (item.get("color") or "").strip().lower() == color_l

    # Check hands first — most common case
    if _matches(session.right_hand):
        return session.right_hand
    if _matches(session.left_hand):
        return session.left_hand

    # Then full inventory (worn slots + container contents)
    for item in (getattr(session, "inventory", []) or []):
        if _matches(item):
            return item

    return None


def _find_worn_or_held(session, target: str):
    """
    Find an item worn or held by the player matching <target>.
    Checks: held (right/left hand), then worn slots.
    Returns item dict or None.
    """
    inv = getattr(session, "inventory", []) or []
    target_l = target.strip().lower()

    # Search worn + held items that have a worn_location
    candidates = [i for i in inv if i.get("worn_location") or i.get("slot") in ("right_hand", "left_hand")]
    for item in candidates:
        name = (item.get("name") or "").lower()
        noun = (item.get("noun") or "").lower()
        short = (item.get("short_name") or "").lower()
        if target_l in name or target_l == noun or target_l in short:
            return item
    return None


async def cmd_dye(session, cmd, args, server):
    """DYE <item> <color|REMOVE>  or  DYE HAIR <color|REMOVE>  or  DYE COLORS"""
    if not args:
        await _show_usage(session)
        return

    parts = args.split()

    # ── DYE COLORS ────────────────────────────────────────────────────────────
    if parts[0].lower() == "colors":
        await cmd_dye_colors(session, cmd, "", server)
        return

    # ── DYE HAIR ──────────────────────────────────────────────────────────────
    if parts[0].lower() == "hair":
        if len(parts) < 2:
            await session.send_line("  Usage: DYE HAIR <color>  or  DYE HAIR REMOVE")
            return

        color_raw = " ".join(parts[1:])

        if color_raw.lower() == "remove":
            old = getattr(session, "hair_color", "brown") or "brown"
            session.hair_color = "brown"
            await _save_hair(session, server)
            await session.send_line(colorize(
                f"  The dye is stripped from your hair, restoring its natural color.",
                TextPresets.SYSTEM
            ))
            return

        color = _normalize_color(color_raw)
        if color not in VALID_COLORS:
            await session.send_line(
                f"  '{color_raw}' is not a recognized dye color.  "
                f"Type DYE COLORS for a full list."
            )
            return

        vial = _find_dye_vial(session, color)
        if not vial:
            await session.send_line(colorize(
                f"  You don't have a vial of {color} dye.  "
                f"Visit Chromial the dyer at room 13547 to purchase one.",
                TextPresets.WARNING
            ))
            return

        old_color = getattr(session, "hair_color", "brown") or "brown"
        session.hair_color = color
        await _save_hair(session, server)
        await _consume_vial(session, vial, server)

        await session.send_line(colorize(
            f"  You apply the {color} dye to your hair.",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            f"  Your hair shifts from {old_color} to a rich {color}.",
            TextPresets.ITEM_NAME
        ))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} applies dye to their hair.",
            exclude=session
        )
        return

    # ── DYE <item> <color|REMOVE> ─────────────────────────────────────────────
    if len(parts) < 2:
        await _show_usage(session)
        return

    # Last word (or two for two-word colors) is the color; everything before is the item
    # Try two-word color first
    if len(parts) >= 3 and " ".join(parts[-2:]).lower() in _COLOR_ALIASES or \
       " ".join(parts[-2:]).lower() in VALID_COLORS:
        item_name = " ".join(parts[:-2])
        color_raw = " ".join(parts[-2:])
    else:
        item_name = " ".join(parts[:-1])
        color_raw = parts[-1]

    if not item_name:
        await _show_usage(session)
        return

    target_item = _find_worn_or_held(session, item_name)
    if not target_item:
        await session.send_line(
            f"  You don't seem to be wearing or holding anything matching '{item_name}'."
        )
        return

    if color_raw.lower() == "remove":
        await _apply_remove(session, target_item, server)
        return

    color = _normalize_color(color_raw)
    if color not in VALID_COLORS:
        await session.send_line(
            f"  '{color_raw}' is not a recognized dye color.  "
            f"Type DYE COLORS to see all available colors."
        )
        return

    vial = _find_dye_vial(session, color)
    if not vial:
        await session.send_line(colorize(
            f"  You don't have a vial of {color} dye.  "
            f"Visit Chromial the dyer at room 13547 to purchase one.",
            TextPresets.WARNING
        ))
        return

    await _apply_dye(session, target_item, color, vial, server)


async def _apply_dye(session, item, color, vial, server):
    """Apply color to an inventory item and consume the vial."""
    old_color = (item.get("color") or "").strip() or "its natural color"
    full_name  = item.get("name") or item.get("short_name") or "item"
    noun       = item.get("noun") or "item"

    # Update color in the item dict (runtime)
    item["color"] = color

    # Build new display name — replace existing color word if present, else prepend
    base_name = item.get("base_name") or item.get("short_name") or full_name
    new_name  = _recolor_name(base_name, old_color, color)
    item["name"] = new_name

    # Persist via extra_data
    inv_id = item.get("inv_id")
    if inv_id and server.db:
        try:
            _update_item_color(server, inv_id, color, new_name)
        except Exception as e:
            log.error("DYE: failed to save color for inv_id %s: %s", inv_id, e)

    await _consume_vial(session, vial, server)

    await session.send_line(colorize(
        f"  You carefully apply the {color} dye to your {noun}.",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        f"  It is now {new_name}.",
        TextPresets.ITEM_NAME
    ))
    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} applies dye to {_pronoun(session)} {noun}.",
        exclude=session
    )


async def _apply_remove(session, item, server):
    """Strip dye from an item, restoring base name."""
    noun      = item.get("noun") or "item"
    base_name = item.get("base_name") or item.get("short_name") or item.get("name") or "item"

    item["color"] = None
    item["name"]  = base_name

    inv_id = item.get("inv_id")
    if inv_id and server.db:
        try:
            _update_item_color(server, inv_id, None, base_name)
        except Exception as e:
            log.error("DYE REMOVE: failed to save color for inv_id %s: %s", inv_id, e)

    await session.send_line(colorize(
        f"  You strip the dye from your {noun}, restoring its natural appearance.",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        f"  It is now {base_name}.",
        TextPresets.ITEM_NAME
    ))


def _update_item_color(server, inv_id: int, color, new_name: str):
    """Persist color and display name into character_inventory.extra_data."""
    import json
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT extra_data FROM character_inventory WHERE id = %s",
            (inv_id,)
        )
        row = cur.fetchone()
        extra = {}
        if row and row["extra_data"]:
            try:
                extra = json.loads(row["extra_data"])
            except Exception:
                extra = {}
        if color:
            extra["color"]    = color
            extra["dye_name"] = new_name
        else:
            extra.pop("color",    None)
            extra.pop("dye_name", None)
        cur.execute(
            "UPDATE character_inventory SET color = %s, extra_data = %s WHERE id = %s",
            (color, json.dumps(extra) if extra else None, inv_id)
        )
        conn.commit()
    finally:
        conn.close()


async def _save_hair(session, server):
    """Persist hair_color to the characters table."""
    if not server.db or not session.character_id:
        return
    try:
        conn = server.db._get_conn()
        cur  = conn.cursor()
        cur.execute(
            "UPDATE characters SET hair_color = %s WHERE id = %s",
            (session.hair_color, session.character_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.error("DYE HAIR: failed to save hair_color: %s", e)


async def _consume_vial(session, vial, server):
    """Remove the consumed dye vial from inventory and hands."""
    inv_id = vial.get("inv_id")
    if not inv_id:
        # No DB record — just clear from hands if present
        if session.right_hand is vial:
            session.right_hand = None
        elif session.left_hand is vial:
            session.left_hand = None
        return

    if server.db:
        try:
            conn = server.db._get_conn()
            cur  = conn.cursor()
            cur.execute("DELETE FROM character_inventory WHERE id = %s", (inv_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            log.error("DYE: failed to remove vial inv_id %s: %s", inv_id, e)

    # Clear from whichever hand is holding it
    if session.right_hand and session.right_hand.get("inv_id") == inv_id:
        session.right_hand = None
    elif session.left_hand and session.left_hand.get("inv_id") == inv_id:
        session.left_hand = None

    # Also strip from inventory list (handles container-stored vials)
    inv = getattr(session, "inventory", []) or []
    session.inventory = [i for i in inv if i.get("inv_id") != inv_id]


def _recolor_name(base_name: str, old_color: str, new_color: str) -> str:
    """
    Replace the color word in a base item name, or prepend it if no color found.
    e.g. "a black leather vest" + new_color "blue" -> "a blue leather vest"
         "a leather vest"       + new_color "blue" -> "a blue leather vest"
    """
    name_l = base_name.lower()
    # Try removing existing color from all known colors
    for c in sorted(VALID_COLORS, key=len, reverse=True):
        if f" {c} " in name_l or name_l.startswith(f"{c} ") or name_l.endswith(f" {c}"):
            base_name = base_name.replace(c, new_color, 1)
            return base_name
    # No color word found — insert after article
    for article in ("a ", "an ", "the ", "some "):
        if base_name.lower().startswith(article):
            return article + new_color + " " + base_name[len(article):]
    return new_color + " " + base_name


def _pronoun(session) -> str:
    gender = getattr(session, "gender", "female") or "female"
    return "her" if gender.lower() in ("female", "f") else "his"


async def _show_usage(session):
    await session.send_line("")
    await session.send_line(colorize("  DYE — Color an item or your hair", TextPresets.SYSTEM))
    await session.send_line("  ─────────────────────────────────────────────")
    await session.send_line("  DYE <item> <color>     Dye a worn or held item")
    await session.send_line("  DYE <item> REMOVE      Strip dye from an item")
    await session.send_line("  DYE HAIR <color>       Dye your hair")
    await session.send_line("  DYE HAIR REMOVE        Restore natural hair color")
    await session.send_line("  DYE COLORS             List all available colors")
    await session.send_line("")
    await session.send_line("  Examples:")
    await session.send_line("    DYE cloak crimson")
    await session.send_line("    DYE armor midnight blue")
    await session.send_line("    DYE boots REMOVE")
    await session.send_line("    DYE HAIR periwinkle")
    await session.send_line("")
    await session.send_line("  Requires one matching dye vial from your inventory.")
    await session.send_line("  Purchase dye vials from Chromial at Ta'Vaalor Dye Wares.")
    await session.send_line("")


async def cmd_dye_colors(session, cmd, args, server):
    """DYE COLORS — list every available dye color."""
    await session.send_line("")
    await session.send_line(colorize("  Available Dye Colors", TextPresets.SYSTEM))
    await session.send_line("  ─────────────────────────────────────────────")
    line = ""
    for i, c in enumerate(sorted(VALID_COLORS), 1):
        line += f"  {c:<18}"
        if i % 4 == 0:
            await session.send_line(line)
            line = ""
    if line.strip():
        await session.send_line(line)
    await session.send_line("")
    await session.send_line("  Purchase dye vials from Chromial at Ta'Vaalor Dye Wares (room 13547).")
    await session.send_line("")
