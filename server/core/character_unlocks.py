"""Persistent character unlock helpers for trainer-taught content."""

from __future__ import annotations


def normalize_unlock_key(raw: str | None) -> str:
    return str(raw or "").strip().lower()


def load_unlocks_for_session(session, db=None) -> dict:
    db = db or getattr(getattr(session, "server", None), "db", None)
    if not db or not getattr(session, "character_id", None):
        session.unlocks = {}
        return {}
    session.unlocks = db.load_character_unlocks(session.character_id) or {}
    return session.unlocks


def has_unlock(session, unlock_key: str) -> bool:
    key = normalize_unlock_key(unlock_key)
    if not key:
        return False
    unlocks = getattr(session, "unlocks", {}) or {}
    return key in unlocks


def grant_unlock(session, server, unlock_key: str, *, unlock_type: str = "generic", notes: str | None = None) -> bool:
    key = normalize_unlock_key(unlock_key)
    if not key:
        return False
    if has_unlock(session, key):
        return True
    db = getattr(server, "db", None)
    if not db or not getattr(session, "character_id", None):
        return False
    if not db.save_character_unlock(session.character_id, key, unlock_type=unlock_type, notes=notes):
        return False
    unlocks = dict(getattr(session, "unlocks", {}) or {})
    unlocks[key] = {
        "unlock_type": str(unlock_type or "generic").strip().lower(),
        "notes": str(notes or "").strip(),
    }
    session.unlocks = unlocks
    return True
