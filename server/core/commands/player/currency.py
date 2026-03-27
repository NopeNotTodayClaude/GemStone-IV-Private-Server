"""
currency.py
-----------
Helpers for liquid-funds handling in shops and custom orders.

Liquid funds include:
  - silver coins on hand
  - bank notes currently held in either hand
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def _fmt(amount: int) -> str:
    return f"{int(amount):,}"


def _note_name(value: int) -> str:
    return f"a bank note worth {_fmt(value)} silvers"


def _held_notes(session) -> List[Tuple[str, dict, int]]:
    notes = []
    for hand in ("right_hand", "left_hand"):
        item = getattr(session, hand, None)
        if item and item.get("item_type") == "bank_note":
            value = max(0, int(item.get("value", 0) or 0))
            notes.append((hand, item, value))
    return notes


def liquid_funds(session) -> int:
    total = int(getattr(session, "silver", 0) or 0)
    for _, _, value in _held_notes(session):
        total += value
    return total


def liquid_funds_text(session) -> str:
    silver = int(getattr(session, "silver", 0) or 0)
    note_total = sum(value for _, _, value in _held_notes(session))
    total = silver + note_total
    if note_total > 0:
        return (
            f"{_fmt(total)} in liquid funds "
            f"({_fmt(silver)} silver, {_fmt(note_total)} in notes)"
        )
    return f"{_fmt(total)} silver"


def _simulate_spend(session, amount: int) -> Dict:
    amount = max(0, int(amount or 0))
    silver_on_hand = int(getattr(session, "silver", 0) or 0)
    silver_spent = min(silver_on_hand, amount)
    remaining = amount - silver_spent

    note_remaining: Dict[str, int] = {}
    note_spent = 0
    notes_used = 0
    returned_note_value: Optional[int] = None

    for hand, _item, value in _held_notes(session):
        use = min(value, remaining)
        rem = value - use
        note_remaining[hand] = rem
        if use > 0:
            note_spent += use
            notes_used += 1
            if rem > 0:
                returned_note_value = rem
        remaining -= use

    return {
        "ok": remaining <= 0,
        "amount": amount,
        "total_available": liquid_funds(session),
        "silver_spent": silver_spent,
        "note_spent": note_spent,
        "notes_used": notes_used,
        "note_remaining": note_remaining,
        "returned_note_value": returned_note_value,
        "remaining_due": remaining,
    }


def receive_hand_after_payment(session, amount: int) -> Optional[str]:
    if not getattr(session, "right_hand", None):
        return "right_hand"
    if not getattr(session, "left_hand", None):
        return "left_hand"

    sim = _simulate_spend(session, amount)
    if not sim["ok"]:
        return None

    for hand in ("right_hand", "left_hand"):
        item = getattr(session, hand, None)
        if not item:
            return hand
        if item.get("item_type") == "bank_note" and sim["note_remaining"].get(hand, 0) <= 0:
            return hand
    return None


def spend_liquid_funds(session, server, amount: int) -> Dict:
    sim = _simulate_spend(session, amount)
    if not sim["ok"]:
        return sim

    session.silver = int(getattr(session, "silver", 0) or 0) - sim["silver_spent"]

    for hand, note, _value in _held_notes(session):
        rem = sim["note_remaining"].get(hand)
        if rem is None:
            continue
        if rem > 0:
            note["value"] = rem
            note["name"] = _note_name(rem)
            note["short_name"] = "bank note"
            note["noun"] = "note"
            note["article"] = "a"
        else:
            inv_id = note.get("inv_id")
            if inv_id and getattr(server, "db", None):
                try:
                    server.db.remove_item_from_inventory(inv_id)
                except Exception:
                    pass
            if getattr(session, hand, None) is note:
                setattr(session, hand, None)
            inv = getattr(session, "inventory", None)
            if isinstance(inv, list):
                session.inventory = [
                    item for item in inv
                    if item is not note and item.get("inv_id") != inv_id
                ]

    return sim


def describe_payment(sim: Dict) -> str:
    silver_spent = int(sim.get("silver_spent", 0) or 0)
    notes_used = int(sim.get("notes_used", 0) or 0)
    returned_note_value = sim.get("returned_note_value")

    if notes_used <= 0:
        return f"takes your {_fmt(silver_spent)} silver"

    note_label = "bank note" if notes_used == 1 else "bank notes"
    if returned_note_value:
        if silver_spent > 0:
            return (
                f"takes your {_fmt(silver_spent)} silver and your {note_label}, "
                f"then hands a note back worth {_fmt(returned_note_value)} silvers"
            )
        return (
            f"takes your {note_label}, then hands a note back worth "
            f"{_fmt(returned_note_value)} silvers"
        )

    if silver_spent > 0:
        return f"takes your {_fmt(silver_spent)} silver and your {note_label}"
    return f"takes your {note_label}"
