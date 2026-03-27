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

BANK_TELLER_ROOMS = {
    10324,  # Bank of Ta'Vaalor, Lobby
    10325,  # Bank of Ta'Vaalor, Teller
    10326,  # Bank of Ta'Vaalor, Exchange
}

NOTE_THRESHOLD = 4999

TELLER_HELP = """
[Bank of Ta'Vaalor - Teller Commands]
  DEPOSIT {#}            Deposit silver coins.
  DEPOSIT ALL            Deposit all silver you are carrying.
  DEPOSIT NOTE           Deposit a bank note you are holding.
  WITHDRAW {#}           Withdraw silver coins (auto-note above 5000).
  WITHDRAW {#} SILVER    Withdraw as coins only.
  WITHDRAW {#} NOTE      Withdraw as a bank note.
  CHECK BALANCE          Check your current account balance.
"""

BANK_HELP = """
[Bank of Ta'Vaalor - Remote Commands]
  BANK ACCOUNT           View your current account balance.
  BANK DEPOSIT {#|ALL}   Send a runner to deposit silver.
  BANK WITHDRAW {#}      Send a runner to fetch silver coins.
"""


def _at_teller(session):
    return session.current_room and session.current_room.id in BANK_TELLER_ROOMS


def _at_bank_teller(session, server):
    if _at_teller(session):
        return True
    if not session.current_room or not hasattr(server, "npcs"):
        return False
    return server.npcs.get_service_npc_in_room(session.current_room.id, "bank") is not None


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


# ── DEPOSIT ───────────────────────────────────────────────────────────────────

async def cmd_deposit(session, cmd, args, server):
    args = (args or "").strip().lower()

    if not args:
        await session.send_line(TELLER_HELP if _at_bank_teller(session, server) else
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
        await session.send_line(BANK_HELP)
        return

    if sub_lower == "account":
        await session.send_line(
            f"[Bank Account - Bank of Ta'Vaalor]\n"
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

    await session.send_line(f"Unknown bank command.{BANK_HELP}")
