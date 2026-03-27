"""
Bank commands - DEPOSIT, WITHDRAW, CHECK, BANK
GemStone IV style banking system.

Storage:
  characters.silver        - coins on hand
  characters.bank_silver   - account balance
  transaction_log          - every deposit/withdrawal recorded

At a teller room:
  DEPOSIT {amount|ALL|NOTE}          - Deposit coins or a bank note
  WITHDRAW {amount} [SILVER|NOTE]    - Withdraw coins (default) or as a note
  CHECK [BALANCE]                    - View account balance

Remote (urchin runner, anywhere):
  BANK                               - Show help
  BANK ACCOUNT                       - View balance
  BANK DEPOSIT {amount|ALL}          - Remote deposit
  BANK WITHDRAW {amount}             - Remote withdrawal (coins only)
"""

import logging
from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)

NOTE_THRESHOLD = 4999

LOCKER_HELP = """
[Locker Commands]
  LOCKER INFO            View the status of the local public locker.
  LOCKER MANIFEST        List the items currently stored there.
  OPEN LOCKER            Open the locker while near the bank counter or locker room.
  LOOK IN LOCKER         View the locker contents while it is open.
  PUT {item} IN LOCKER   Store an item from your person.
  GET {item} FROM LOCKER Retrieve an item from the open locker.
  INSPECT LOCKER         View capacity and usage details.
  CLOSE LOCKER           Close the locker before leaving.
"""


def _format_teller_help(bank_label: str) -> str:
    return f"""
[{bank_label} - Teller Commands]
  DEPOSIT {{#}}            Deposit silver coins.
  DEPOSIT ALL            Deposit all silver you are carrying.
  DEPOSIT NOTE           Deposit a bank note you are holding.
  WITHDRAW {{#}}           Withdraw silver coins (auto-note above 5000).
  WITHDRAW {{#}} SILVER    Withdraw as coins only.
  WITHDRAW {{#}} NOTE      Withdraw as a bank note.
  CHECK BALANCE          Check your current account balance.
  LOCKER INFO            View the local public locker status.
"""


def _format_bank_help(bank_label: str) -> str:
    return f"""
[{bank_label} - Remote Commands]
  BANK ACCOUNT           View your current account balance.
  BANK DEPOSIT {{#|ALL}}   Send a runner to deposit silver.
  BANK WITHDRAW {{#}}      Send a runner to fetch silver coins.
  LOCKER INFO            View the local public locker status.
"""


def _get_bank_label(session, server) -> str:
    room = getattr(session, "current_room", None)
    if getattr(server, "db", None) and room:
        try:
            location = server.db.get_public_locker_location_for_room(room.id)
            if location and location.get("town_name"):
                return f"Bank of {location['town_name']}"
        except Exception:
            pass
    if room and getattr(room, "title", None):
        return room.title
    return "Bank"


def _at_teller(session):
    return False


def _at_bank_teller(session, server):
    room = getattr(session, "current_room", None)
    if not room:
        return False
    if getattr(server, "db", None):
        try:
            location = server.db.get_public_locker_location_for_room(room.id)
            if location and "bank" in (location.get("roles") or []):
                return True
        except Exception:
            pass
    if not hasattr(server, "npcs"):
        return False
    return server.npcs.get_service_npc_in_room(room.id, "bank") is not None


def _fmt(amount):
    return f"{amount:,}"


def _save(session, server):
    """Persist via the standard full character save (writes silver + bank_silver)."""
    if server.db:
        server.db.save_character(session)


def _log_tx(server, character_id, tx_type, amount, description):
    """Insert a row into transaction_log."""
    if not server.db:
        return
    try:
        server.db.execute_query(
            """INSERT INTO transaction_log
               (character_id, transaction_type, amount, description)
               VALUES (%s, %s, %s, %s)""",
            (character_id, tx_type, amount, description)
        )
    except Exception as e:
        log.error("transaction_log write failed: %s", e)


def _find_note(session):
    for hand in ("right_hand", "left_hand"):
        item = getattr(session, hand, None)
        if item and item.get("item_type") == "bank_note":
            return item, hand
    return None, None


def _get_public_locker_location(session, server):
    room = getattr(session, "current_room", None)
    if not room or not getattr(server, "db", None):
        return None
    try:
        return server.db.get_public_locker_location_for_room(room.id)
    except Exception as e:
        log.error("Failed to resolve locker location for room %s: %s", getattr(room, "id", 0), e)
        return None


def _locker_is_open(session, location):
    return bool(location and getattr(session, "locker_open_location_id", None) == int(location["id"]))


def _locker_is_usable_here(location):
    roles = set((location or {}).get("roles") or [])
    return bool({"locker", "bank"} & roles)


def _get_locker_entry_commands(session, server, location):
    room = getattr(session, "current_room", None)
    if not room or not getattr(server, "db", None) or not location:
        return []
    try:
        locker_room_ids = set(server.db.get_public_locker_room_ids(location["id"], "locker"))
    except Exception:
        locker_room_ids = set()
    commands = []
    for exit_key, target_room_id in (getattr(room, "exits", {}) or {}).items():
        if int(target_room_id or 0) not in locker_room_ids:
            continue
        if exit_key.startswith("go_"):
            commands.append(f"GO {exit_key[3:].replace('_', ' ').upper()}")
        else:
            commands.append(exit_key.replace("_", " ").upper())
    return sorted(dict.fromkeys(commands))


def _get_locker_room_label(server, location):
    if not getattr(server, "db", None) or not getattr(server, "world", None) or not location:
        return None
    try:
        locker_room_ids = server.db.get_public_locker_room_ids(location["id"], "locker")
    except Exception:
        locker_room_ids = []
    for room_id in locker_room_ids:
        room = server.world.get_room(room_id)
        if room and getattr(room, "title", None):
            return room.title
    return None


def _locker_item_label(item):
    return item.get("short_name") or item.get("name") or "something"


def _locker_storage_count(server, character_id, location_id):
    if not getattr(server, "db", None):
        return 0
    return server.db.count_character_locker_items(character_id, location_id)


def _locker_manifest_lines(server, character_id, location):
    items = server.db.get_character_locker_items(character_id, location["id"]) if getattr(server, "db", None) else []
    lines = [
        f"[{location['town_name']} Locker Manifest]",
        f"  Stored items: {len(items)} / {int(location.get('capacity') or 50)}",
    ]
    if not items:
        lines.append("  Your locker is currently empty.")
        return lines
    for idx, item in enumerate(items, 1):
        lines.append(f"  {idx:>2}. {_locker_item_label(item)}")
    return lines


async def cmd_locker(session, cmd, args, server):
    """LOCKER - Public locker info and manifest support."""
    sub = (args or "").strip().lower()
    location = _get_public_locker_location(session, server)

    if not sub or sub == "help":
        await session.send_line(LOCKER_HELP)
        return

    if sub == "info":
        if not location:
            await session.send_line("You are not near a public locker location.")
            return
        count = _locker_storage_count(server, session.character_id, location["id"])
        lines = [
            f"[{location['town_name']} Public Locker]",
            f"  Capacity      : {count} / {int(location.get('capacity') or 50)} items",
            f"  Locker status : {'open' if _locker_is_open(session, location) else 'closed'}",
        ]
        if _locker_is_usable_here(location):
            lines.append("  Access        : OPEN LOCKER")
        else:
            entry_cmds = _get_locker_entry_commands(session, server, location)
            if entry_cmds:
                lines.append("  Entry         : " + ", ".join(entry_cmds))
            else:
                room_label = _get_locker_room_label(server, location)
                if room_label:
                    lines.append(f"  Locker room   : {room_label}")
                lines.append("  Access        : Visit the local locker annex before opening your locker.")
        await session.send_line("\n".join(lines))
        return

    if sub == "manifest":
        if not location:
            await session.send_line("You are not near a public locker location.")
            return
        await session.send_line("\n".join(_locker_manifest_lines(server, session.character_id, location)))
        return

    await session.send_line(LOCKER_HELP)


async def maybe_handle_locker_open(session, target, server):
    if (target or "").strip().lower() != "locker":
        return False
    location = _get_public_locker_location(session, server)
    if not location:
        await session.send_line("You see no locker here.")
        return True
    if not _locker_is_usable_here(location):
        entry_cmds = _get_locker_entry_commands(session, server, location)
        if entry_cmds:
            await session.send_line("You will need to step into the locker first.  Try: " + ", ".join(entry_cmds))
        else:
            room_label = _get_locker_room_label(server, location)
            if room_label:
                await session.send_line(f"You need to be standing inside {room_label} to do that.")
            else:
                await session.send_line("You need to be standing inside the locker room to do that.")
        return True
    if _locker_is_open(session, location):
        await session.send_line("The locker is already open.")
        return True

    session.locker_open_location_id = int(location["id"])
    session.locker_open_town_name = location["town_name"]
    count = _locker_storage_count(server, session.character_id, location["id"])
    capacity = int(location.get("capacity") or 50)
    await session.send_line(
        "As you open the locker, hidden racks and compartments glide into place with quiet mechanical precision.\n"
        f"Your locker is currently holding {count} items out of a maximum of {capacity}."
    )
    return True


async def maybe_handle_locker_close(session, target, server):
    if (target or "").strip().lower() != "locker":
        return False
    location = _get_public_locker_location(session, server)
    if not location or not _locker_is_open(session, location):
        await session.send_line("The locker is already closed.")
        return True
    session.locker_open_location_id = None
    session.locker_open_town_name = None
    await session.send_line("The racks and compartments withdraw smoothly as you close the locker.")
    return True


async def maybe_handle_locker_inspect(session, target, server):
    if (target or "").strip().lower() != "locker":
        return False
    location = _get_public_locker_location(session, server)
    if not location:
        await session.send_line("You see no locker here.")
        return True
    count = _locker_storage_count(server, session.character_id, location["id"])
    capacity = int(location.get("capacity") or 50)
    lines = [
        f"Your locker is currently holding {count} items out of a maximum of {capacity}.",
    ]
    if _locker_is_open(session, location):
        lines.append("The locker stands open, ready to receive or return items.")
    else:
        lines.append("The locker is currently closed.")
    await session.send_line("\n".join(lines))
    return True


async def maybe_handle_locker_look_in(session, target, server):
    if (target or "").strip().lower() != "locker":
        return False
    location = _get_public_locker_location(session, server)
    if not location or not _locker_is_open(session, location):
        await session.send_line("The locker is closed.")
        return True
    await session.send_line("\n".join(_locker_manifest_lines(server, session.character_id, location)))
    return True


def _build_locker_snapshot(session, item):
    from server.core.commands.player.inventory import _get_container_contents

    snapshot = {
        key: value for key, value in dict(item or {}).items()
        if key not in {"inv_id", "slot", "container_id", "locker_item_id", "stored_at"}
    }
    snapshot.pop("locker_item_id", None)
    snapshot.pop("stored_at", None)
    if item.get("item_type") == "container":
        children = []
        for child in _get_container_contents(session, item):
            children.append(_build_locker_snapshot(session, child))
        inline_contents = item.get("contents") or []
        if inline_contents:
            children.extend([dict(x) for x in inline_contents if isinstance(x, dict)])
        if children:
            snapshot["contained_items"] = children
    return snapshot


def _gather_locker_item(session, target):
    from server.core.commands.player.inventory import (
        _ensure_hands,
        _find_in_hands,
        _find_worn,
        _find_loose_item,
        _get_worn_containers,
        _find_in_container,
    )

    _ensure_hands(session)
    item, hand = _find_in_hands(session, target)
    if item:
        return item, hand, None

    item = _find_worn(session, target)
    if item:
        return item, None, "worn"

    item = _find_loose_item(session, target)
    if item:
        return item, None, "loose"

    for cont in _get_worn_containers(session):
        if not cont.get("opened"):
            continue
        item = _find_in_container(session, target, cont)
        if item:
            return item, None, "container"

    return None, None, None


def _collect_inventory_descendants(session, parent_inv_id):
    descendants = []
    queue = [int(parent_inv_id)]
    while queue:
        parent = queue.pop(0)
        for item in list(getattr(session, "inventory", []) or []):
            cid = item.get("container_id")
            try:
                cid = int(cid) if cid is not None else None
            except (TypeError, ValueError):
                cid = None
            if cid == parent and item not in descendants:
                descendants.append(item)
                if item.get("inv_id"):
                    queue.append(int(item["inv_id"]))
    return descendants


def _remove_item_from_session_inventory(session, item, hand=None):
    if hand == "right_hand":
        session.right_hand = None
    elif hand == "left_hand":
        session.left_hand = None
    else:
        if item in session.inventory:
            session.inventory.remove(item)


def _remove_item_tree_from_character(session, server, root_item, hand=None):
    inv_ids = []
    if root_item.get("inv_id"):
        inv_ids.append(int(root_item["inv_id"]))
    descendants = []
    if root_item.get("inv_id"):
        descendants = _collect_inventory_descendants(session, root_item["inv_id"])
        inv_ids.extend(int(item["inv_id"]) for item in descendants if item.get("inv_id"))

    _remove_item_from_session_inventory(session, root_item, hand=hand)
    for child in descendants:
        if child in session.inventory:
            session.inventory.remove(child)

    if inv_ids and getattr(server, "db", None):
        placeholders = ",".join(["%s"] * len(inv_ids))
        server.db.execute_update(
            f"DELETE FROM character_inventory WHERE id IN ({placeholders})",
            tuple(inv_ids),
        )


async def maybe_handle_locker_put(session, item_name, container_name, server):
    if (container_name or "").strip().lower() != "locker":
        return False
    location = _get_public_locker_location(session, server)
    if not location or not _locker_is_open(session, location):
        await session.send_line("You need to OPEN LOCKER first.")
        return True

    item, hand, _ = _gather_locker_item(session, item_name)
    if not item:
        await session.send_line("I could not find what you were referring to.")
        return True

    current_count = _locker_storage_count(server, session.character_id, location["id"])
    capacity = int(location.get("capacity") or 50)
    if current_count >= capacity:
        await session.send_line("Your locker is full.")
        return True

    snapshot = _build_locker_snapshot(session, item)
    locker_row_id = server.db.save_character_locker_item(session.character_id, location["id"], snapshot)
    if not locker_row_id:
        await session.send_line("Your locker resists the attempt, refusing to accept the item.")
        return True

    _remove_item_tree_from_character(session, server, item, hand=hand)

    item_name_disp = item.get("short_name") or item.get("name") or "something"
    await session.send_line(f"You place {item_name_disp} in the locker, and it quickly disappears from sight.")
    return True


def _find_locker_item(items, target):
    from server.core.commands.player.inventory import _match_target

    if not target:
        return None
    target = target.strip().lower()
    if target.isdigit():
        idx = int(target)
        if 1 <= idx <= len(items):
            return items[idx - 1]
    for item in items:
        if _match_target(item, target):
            return item
    return None


def _restore_locker_snapshot(session, server, snapshot, *, slot=None, container_inv_id=None):
    item_id = snapshot.get("item_id") or snapshot.get("id")
    if not item_id:
        return None

    inv_id = server.db.insert_inventory_item_instance(
        session.character_id,
        item_id,
        slot=slot,
        quantity=int(snapshot.get("quantity") or 1),
        container_id=container_inv_id,
    )
    if not inv_id:
        return None

    item = {key: value for key, value in dict(snapshot).items() if key != "contained_items"}
    item["inv_id"] = inv_id
    item["slot"] = None if container_inv_id is not None else slot
    item["container_id"] = container_inv_id

    extra = {
        key: value for key, value in dict(snapshot).items()
        if key not in {
            "item_id", "id", "name", "short_name", "noun", "article", "item_type",
            "weight", "value", "worn_location", "description", "examine_text",
            "lore_text", "material", "color", "weapon_type", "weapon_category",
            "attack_bonus", "damage_bonus", "damage_factor", "weapon_speed",
            "damage_type", "level_required", "armor_group", "armor_asg",
            "defense_bonus", "enchant_bonus", "spell_hindrance", "action_penalty",
            "shield_ds", "shield_size", "shield_evade_penalty", "container_capacity",
            "lockpick_modifier", "contained_items",
        }
    }
    if extra:
        server.db.save_item_extra_data(inv_id, extra)

    if slot == "right_hand":
        session.right_hand = item
    elif slot == "left_hand":
        session.left_hand = item
    else:
        session.inventory.append(item)

    for child in snapshot.get("contained_items", []) or []:
        _restore_locker_snapshot(session, server, child, container_inv_id=inv_id)

    return item


async def maybe_handle_locker_get(session, target, source_name, server):
    if (source_name or "").strip().lower() != "locker":
        return False
    location = _get_public_locker_location(session, server)
    if not location or not _locker_is_open(session, location):
        await session.send_line("You need to OPEN LOCKER first.")
        return True

    items = server.db.get_character_locker_items(session.character_id, location["id"])
    item = _find_locker_item(items, target)
    if not item:
        await session.send_line("You do not see that in your locker.")
        return True

    slot = None
    if getattr(session, "right_hand", None) is None:
        slot = "right_hand"
    elif getattr(session, "left_hand", None) is None:
        slot = "left_hand"

    restored = _restore_locker_snapshot(session, server, item, slot=slot)
    if not restored:
        await session.send_line("The locker shudders, but fails to release the item properly.")
        return True

    server.db.remove_character_locker_item(item["locker_item_id"])
    item_name_disp = item.get("short_name") or item.get("name") or "something"
    if slot:
        await session.send_line(f"You remove {item_name_disp} from the locker.")
    else:
        await session.send_line(
            f"You remove {item_name_disp} from the locker, but with both hands occupied you are forced to tuck it in with your other belongings."
        )
    return True


async def maybe_handle_locker_leave(session, server):
    location = _get_public_locker_location(session, server)
    if not location:
        return False
    if not _locker_is_open(session, location):
        return False
    await session.send_line("You should CLOSE LOCKER before leaving.")
    return True


# ── DEPOSIT ───────────────────────────────────────────────────────────────────

async def cmd_deposit(session, cmd, args, server):
    args = (args or "").strip().lower()

    if not args:
        await session.send_line(_format_teller_help(_get_bank_label(session, server)) if _at_bank_teller(session, server) else
                                "Deposit what?  Try: DEPOSIT 500, DEPOSIT ALL, or DEPOSIT NOTE")
        return

    if args == "note":
        note, hand = _find_note(session)
        if not note:
            await session.send_line("You are not holding any bank notes.")
            return
        value = note.get("value", 0)
        if value <= 0:
            await session.send_line("That note doesn't appear to be worth anything.")
            return
        if server.db:
            inv_id = note.get("inv_id")
            if inv_id:
                server.db.remove_item_from_inventory(inv_id)
        setattr(session, hand, None)
        session.bank_silver += value
        _save(session, server)
        _log_tx(server, session.character_id, "bank_deposit", value,
                f"Bank note deposit of {value} silver")
        await session.send_line(
            f"You present the bank note to the teller, who verifies and records the amount.\n"
            f'The teller says, "I\'ve credited {_fmt(value)} silvers to your account, '
            f'{session.character_name}.  Your new balance is {_fmt(session.bank_silver)} silvers."'
        )
        return

    if args == "all":
        amount = session.silver
        if amount <= 0:
            await session.send_line("You have no silver to deposit.")
            return
    else:
        try:
            amount = int(args.replace(",", ""))
        except ValueError:
            await session.send_line("Deposit how much?  Try: DEPOSIT 500 or DEPOSIT ALL")
            return
        if amount <= 0:
            await session.send_line("You must specify a positive amount.")
            return
        if amount > session.silver:
            await session.send_line(f"You only have {_fmt(session.silver)} silver on you.")
            return

    session.silver -= amount
    session.bank_silver += amount
    _save(session, server)
    _log_tx(server, session.character_id, "bank_deposit", amount,
            f"Teller deposit of {amount} silver")
    await session.send_line(
        f"You slide {_fmt(amount)} silvers across the counter.  The teller counts carefully and nods.\n"
        f'She says, "Thank you, {session.character_name}.  '
        f'Your new balance is {_fmt(session.bank_silver)} silvers.  Have a pleasant day!"'
    )


# ── WITHDRAW ──────────────────────────────────────────────────────────────────

async def cmd_withdraw(session, cmd, args, server):
    args = (args or "").strip()
    if not args:
        await session.send_line("Withdraw how much?  Try: WITHDRAW 500 or WITHDRAW 5000 NOTE")
        return

    parts = args.lower().split()
    try:
        amount = int(parts[0].replace(",", ""))
    except ValueError:
        await session.send_line("Withdraw how much?  Try: WITHDRAW 500")
        return

    if amount <= 0:
        await session.send_line("You must specify a positive amount.")
        return
    if amount > session.bank_silver:
        await session.send_line(f"Your account only contains {_fmt(session.bank_silver)} silvers.")
        return

    as_note = amount > NOTE_THRESHOLD
    if len(parts) > 1:
        if parts[1] == "note":
            as_note = True
        elif parts[1] == "silver":
            as_note = False
        else:
            await session.send_line("Format must be SILVER or NOTE.  Example: WITHDRAW 1000 NOTE")
            return

    if as_note:
        if session.right_hand and session.left_hand:
            await session.send_line("Your hands are full!  Free a hand first.")
            return
        session.bank_silver -= amount
        _save(session, server)
        _log_tx(server, session.character_id, "bank_withdraw", amount,
                f"Bank note withdrawal of {amount} silver")
        note_item = {
            "inv_id": None, "item_id": None, "item_type": "bank_note",
            "name": f"a bank note worth {_fmt(amount)} silvers",
            "short_name": "bank note", "noun": "note", "article": "a",
            "value": amount, "weight": 0, "slot": None,
        }
        hand = "right_hand" if not session.right_hand else "left_hand"
        setattr(session, hand, note_item)
        await session.send_line(
            f'The teller writes out a note for {_fmt(amount)} silvers and slides it across the counter.\n'
            f"You are now holding a bank note worth {_fmt(amount)} silvers.\n"
            f"Remaining balance: {_fmt(session.bank_silver)} silvers."
        )
    else:
        session.bank_silver -= amount
        session.silver += amount
        _save(session, server)
        _log_tx(server, session.character_id, "bank_withdraw", amount,
                f"Coin withdrawal of {amount} silver")
        await session.send_line(
            f'The teller counts out {_fmt(amount)} silvers and pushes them across the counter.\n'
            f"You receive {_fmt(amount)} silvers.\n"
            f"Remaining balance: {_fmt(session.bank_silver)} silvers."
        )


# ── CHECK ─────────────────────────────────────────────────────────────────────

async def cmd_check(session, cmd, args, server):
    args = (args or "").strip().lower()
    if args and args != "balance":
        await session.send_line("Check what?  Try: CHECK BALANCE")
        return
    if _at_bank_teller(session, server):
        await session.send_line(
            f'The teller consults the ledger and says, "Your current balance is '
            f'{_fmt(session.bank_silver)} silvers, {session.character_name}."'
        )
    else:
        await session.send_line(
            f"[Bank Account]\n"
            f"  Account balance : {_fmt(session.bank_silver)} silvers\n"
            f"  Silver on hand  : {_fmt(session.silver)} silvers"
        )


# ── BANK (remote verb) ────────────────────────────────────────────────────────

async def cmd_bank(session, cmd, args, server):
    sub = (args or "").strip()
    sub_lower = sub.lower()

    if not sub_lower or sub_lower == "help":
        await session.send_line(_format_bank_help(_get_bank_label(session, server)))
        return

    if sub_lower == "account":
        await session.send_line(
            f"[Bank Account - {_get_bank_label(session, server)}]\n"
            f"  Account balance : {_fmt(session.bank_silver)} silvers\n"
            f"  Silver on hand  : {_fmt(session.silver)} silvers"
        )
        return

    if sub_lower.startswith("deposit"):
        rest = sub[7:].strip()
        if not rest:
            await session.send_line("Deposit how much?  Try: BANK DEPOSIT 500 or BANK DEPOSIT ALL")
            return
        if rest.lower() == "all":
            amount = session.silver
        else:
            try:
                amount = int(rest.replace(",", ""))
            except ValueError:
                await session.send_line("Deposit how much?  Try: BANK DEPOSIT 500")
                return
        if amount <= 0:
            await session.send_line("You must specify a positive amount.")
            return
        if amount > session.silver:
            await session.send_line(f"You only have {_fmt(session.silver)} silver on you.")
            return
        session.silver -= amount
        session.bank_silver += amount
        _save(session, server)
        _log_tx(server, session.character_id, "bank_deposit", amount,
                f"Remote runner deposit of {amount} silver")
        await session.send_line(
            f"You flag down a street urchin and hand over {_fmt(amount)} silvers "
            f"with instructions to deposit them at the bank.\n"
            f"The urchin returns shortly with a receipt.\n"
            f"Your new balance is {_fmt(session.bank_silver)} silvers."
        )
        return

    if sub_lower.startswith("withdraw"):
        rest = sub[8:].strip()
        if not rest:
            await session.send_line("Withdraw how much?  Try: BANK WITHDRAW 500")
            return
        try:
            amount = int(rest.split()[0].replace(",", ""))
        except ValueError:
            await session.send_line("Withdraw how much?  Try: BANK WITHDRAW 500")
            return
        if amount <= 0:
            await session.send_line("You must specify a positive amount.")
            return
        if amount > session.bank_silver:
            await session.send_line(f"Your account only contains {_fmt(session.bank_silver)} silvers.")
            return
        session.bank_silver -= amount
        session.silver += amount
        _save(session, server)
        _log_tx(server, session.character_id, "bank_withdraw", amount,
                f"Remote runner withdrawal of {amount} silver")
        await session.send_line(
            f"You send a street urchin to the bank with your withdrawal request.\n"
            f"The urchin returns shortly and counts out {_fmt(amount)} silvers into your hand.\n"
            f"Remaining balance: {_fmt(session.bank_silver)} silvers."
        )
        return

    await session.send_line(f"Unknown bank command.{_format_bank_help(_get_bank_label(session, server))}")
