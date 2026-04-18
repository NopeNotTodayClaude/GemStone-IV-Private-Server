"""
npc_placement_alias_loader.py
-----------------------------
Loads resolver-side NPC placement aliases from scripts/data/npc_placement_aliases.lua.

This keeps content-specific placement knowledge in Lua data instead of Python
conditionals.
"""

from __future__ import annotations

import logging
import os
import re

log = logging.getLogger(__name__)


def _parse_list_sections(text: str, section_names: list[str]) -> dict[str, dict[str, list[str]]]:
    sections: dict[str, dict[str, list[str]]] = {name: {} for name in section_names}
    lines = text.splitlines()
    current_section = None
    current_key = None
    current_values: list[str] = []

    for raw_line in lines:
        line = str(raw_line or "").strip()
        if not line or line.startswith("--"):
            continue

        if current_section is None:
            for section_name in section_names:
                if re.match(rf"^{re.escape(section_name)}\s*=\s*\{{$", line):
                    current_section = section_name
                    current_key = None
                    current_values = []
                    break
            continue

        if current_key is None:
            if line == "},":
                current_section = None
                continue
            match = re.match(r'^\["([^"]+)"\]\s*=\s*\{$', line)
            if match:
                current_key = str(match.group(1) or "").strip()
                current_values = []
            continue

        if line == "},":
            if current_key and current_values:
                sections.setdefault(current_section, {})[current_key] = list(current_values)
            current_key = None
            current_values = []
            continue

        for item in re.findall(r'"([^"]+)"', line):
            value = str(item or "").strip()
            if value:
                current_values.append(value)

    return sections


def load_npc_placement_aliases(scripts_path: str) -> dict[str, dict[str, list[str]]]:
    data_path = os.path.join(scripts_path, "data", "npc_placement_aliases.lua")
    if not os.path.isfile(data_path):
        return {
            "affiliation_aliases": {},
            "affiliation_room_tags": {},
            "affiliation_room_titles": {},
            "location_hint_room_titles": {},
            "template_room_prefixes": {},
            "template_room_titles_override_hint": {},
            "template_room_titles": {},
            "role_room_tags": {},
        }

    try:
        with open(data_path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except Exception as exc:
        log.warning("npc_placement_alias_loader: failed reading %s (%s)", data_path, exc)
        return {
            "affiliation_aliases": {},
            "affiliation_room_tags": {},
            "affiliation_room_titles": {},
            "location_hint_room_titles": {},
            "template_room_prefixes": {},
            "template_room_titles_override_hint": {},
            "template_room_titles": {},
            "role_room_tags": {},
        }

    sections = _parse_list_sections(
        text,
        [
            "affiliation_aliases",
            "affiliation_room_tags",
            "affiliation_room_titles",
            "location_hint_room_titles",
            "template_room_prefixes",
            "template_room_titles_override_hint",
            "template_room_titles",
            "role_room_tags",
        ],
    )

    log.info(
        "npc_placement_alias_loader: loaded %d affiliation alias rows, %d room-tag rows, %d room-title rows, %d hint-title rows, %d template-prefix rows, %d override-title rows, %d template-title rows, %d role-tag rows",
        len(sections.get("affiliation_aliases") or {}),
        len(sections.get("affiliation_room_tags") or {}),
        len(sections.get("affiliation_room_titles") or {}),
        len(sections.get("location_hint_room_titles") or {}),
        len(sections.get("template_room_prefixes") or {}),
        len(sections.get("template_room_titles_override_hint") or {}),
        len(sections.get("template_room_titles") or {}),
        len(sections.get("role_room_tags") or {}),
    )
    return {
        "affiliation_aliases": dict(sections.get("affiliation_aliases") or {}),
        "affiliation_room_tags": dict(sections.get("affiliation_room_tags") or {}),
        "affiliation_room_titles": dict(sections.get("affiliation_room_titles") or {}),
        "location_hint_room_titles": dict(sections.get("location_hint_room_titles") or {}),
        "template_room_prefixes": dict(sections.get("template_room_prefixes") or {}),
        "template_room_titles_override_hint": dict(sections.get("template_room_titles_override_hint") or {}),
        "template_room_titles": dict(sections.get("template_room_titles") or {}),
        "role_room_tags": dict(sections.get("role_room_tags") or {}),
    }
