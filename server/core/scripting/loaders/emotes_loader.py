"""
emotes_loader.py
----------------
Loads emote definitions from scripts/data/emotes.lua.

Returns a list of dicts, each with:
  verb         - command string
  self         - message to actor (no target)
  room         - message to room  (no target)   {name}
  self_t       - message to actor (with target)  {name} {target}
  target_t     - message to target               {name} {target}
  room_t       - message to room  (with target)  {name} {target}

Returns None if Lua is unavailable or load fails.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

_REQUIRED = ("verb", "self", "room")


def load_emotes(lua_engine) -> Optional[list]:
    if not lua_engine or not lua_engine.available:
        return None
    try:
        data = lua_engine.load_data("data/emotes")
        if not data:
            return None

        raw_list = data.get("list") if isinstance(data, dict) else None
        if not raw_list:
            log.warning("emotes_loader: 'list' key missing from emotes.lua")
            return None

        emotes = []
        seen_verbs = set()

        for entry in raw_list:
            if not isinstance(entry, dict):
                continue
            # Skip sentinel duplicate entries
            if entry.get("skip"):
                continue
            verb = str(entry.get("verb", "")).strip().lower()
            if not verb or verb in seen_verbs:
                continue
            # Must have at minimum verb + self + room
            if not all(entry.get(k) for k in _REQUIRED):
                continue
            seen_verbs.add(verb)
            emotes.append({
                "verb":     verb,
                "self":     str(entry["self"]),
                "room":     str(entry["room"]),
                "self_t":   str(entry.get("self_t",  entry["self"])),
                "target_t": str(entry.get("target_t", entry["room"])),
                "room_t":   str(entry.get("room_t",  entry["room"])),
            })

        log.info("emotes_loader: loaded %d emotes from Lua", len(emotes))
        return emotes

    except Exception as e:
        log.warning("emotes_loader: failed: %s", e)
        return None
