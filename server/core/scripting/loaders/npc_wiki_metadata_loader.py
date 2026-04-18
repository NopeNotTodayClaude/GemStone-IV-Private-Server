"""
npc_wiki_metadata_loader.py
---------------------------
Loads generated NPC wiki metadata from scripts/data/npc_wiki_metadata.lua.

The generated file is a regular text export, not executable Lua, so this
loader parses its record structure directly and sanitizes template boilerplate
before returning placement-safe metadata.
"""

from __future__ import annotations

import logging
import os
import re

log = logging.getLogger(__name__)

_CACHE_KEY = None
_CACHE_ROWS: dict[str, dict] = {}

_LIST_FIELDS = {"venues", "storylines", "shop_links"}
_SCALAR_FIELDS = {"wiki_template", "hometown", "profession", "service", "affiliation"}

_DROP_EXACT = {
    "",
    "}}",
    "only use if more than one venue",
    "what events do they frequent",
    "what festivals do they frequent",
    "what festivals do the frequent.",
    "where does this npc call home?",
    "add storyline2, storyline3, and storyline4 fields on a new line, as appropriate",
    "add storyline2, storyline3, storyline4, and up to storyline9 fields on a new line, as appropriate",
}

_TRIM_MARKERS = (
    " where does this npc call home?",
    "where does this npc call home?",
    " what events do they frequent",
    "what events do they frequent",
    " what festivals do they frequent",
    "what festivals do they frequent",
    " what festivals do the frequent",
    "what festivals do the frequent",
    " please only use ",
    "please only use ",
    " only use if more than one venue",
    "only use if more than one venue",
    " if more than three, list the top three or wandering",
    "if more than three, list the top three or wandering",
    " if more than three, list the top three",
    "if more than three, list the top three",
    " if citizen merchant list town under town.",
    "if citizen merchant list town under town.",
    " if citizen merchant list town.",
    "if citizen merchant list town.",
    " an example would be citizen-only merchant",
    "an example would be citizen-only merchant",
    " use other is necessary",
    "use other is necessary",
    " add storyline2",
    "add storyline2",
    " add storyline3",
    "add storyline3",
    " add storyline4",
    "add storyline4",
    " add storyline5",
    "add storyline5",
    " add storyline6",
    "add storyline6",
    " add storyline7",
    "add storyline7",
    " add storyline8",
    "add storyline8",
    " add storyline9",
    "add storyline9",
)

_DROP_CONTAINS = (
    "what events do they frequent",
    "what festivals do they frequent",
    "where does this npc call home?",
)


def _clean_text(value: str) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return ""
    text = text.replace('\\"', '"').replace("\\'", "'")
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = text.replace("'''", "")
    text = text.replace("_", " ")
    if "|" in text:
        parts = [part.strip() for part in text.split("|") if str(part or "").strip()]
        if parts:
            text = parts[-1]
    text = text.replace("{{", " ").replace("}}", " ")
    text = re.sub(r"\s+", " ", text).strip(" ,;|-")
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1].strip()
    lowered = text.lower()
    for marker in _TRIM_MARKERS:
        index = lowered.find(marker)
        if index >= 0:
            text = text[:index]
            lowered = text.lower()
    text = re.sub(r"\s+", " ", text).strip(" ,;|-")
    lowered = text.lower()
    if lowered in _DROP_EXACT:
        return ""
    if any(snippet in lowered for snippet in _DROP_CONTAINS):
        return ""
    return text


def _clean_list(values) -> list[str]:
    cleaned = []
    seen = set()
    for raw in values or ():
        value = _clean_text(raw)
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        cleaned.append(value)
    return cleaned


def _cache_key_for(path: str):
    try:
        stat = os.stat(path)
    except OSError:
        return None
    return (os.path.abspath(path), int(stat.st_mtime_ns), int(stat.st_size))


def load_npc_wiki_metadata(scripts_path: str) -> dict[str, dict]:
    global _CACHE_KEY, _CACHE_ROWS
    data_path = os.path.join(scripts_path, "data", "npc_wiki_metadata.lua")
    if not os.path.isfile(data_path):
        return {}

    cache_key = _cache_key_for(data_path)
    if cache_key and cache_key == _CACHE_KEY:
        return _CACHE_ROWS

    try:
        with open(data_path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except Exception as exc:
        log.warning("npc_wiki_metadata_loader: failed reading %s (%s)", data_path, exc)
        return {}

    rows: dict[str, dict] = {}
    current_id = None
    current = None

    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("--") or stripped == "return {" or stripped == "}":
            continue

        record_start = re.match(r'^"([^"]+)"\s*=\s*\{$', stripped)
        if record_start:
            current_id = str(record_start.group(1) or "").strip()
            current = {"venues": [], "storylines": [], "shop_links": []}
            continue

        if stripped == "},":
            if current_id and current is not None:
                normalized = {}
                for field in _SCALAR_FIELDS:
                    normalized[field] = _clean_text(current.get(field, ""))
                for field in _LIST_FIELDS:
                    normalized[field] = _clean_list(current.get(field, []))
                if any(normalized.get(field) for field in ("hometown", "venues", "shop_links", "storylines")):
                    rows[current_id] = normalized
            current_id = None
            current = None
            continue

        if current is None:
            continue

        scalar_match = re.match(r'^(\w+)\s*=\s*"((?:\\"|[^"])*)",?$', stripped)
        if scalar_match:
            field = str(scalar_match.group(1) or "").strip()
            if field in _SCALAR_FIELDS:
                current[field] = scalar_match.group(2)
            continue

        list_match = re.match(r'^(\w+)\s*=\s*\{(.*)\},?$', stripped)
        if list_match:
            field = str(list_match.group(1) or "").strip()
            if field in _LIST_FIELDS:
                current[field] = re.findall(r'"((?:\\"|[^"])*)"', list_match.group(2))
            continue

    _CACHE_KEY = cache_key
    _CACHE_ROWS = rows
    log.info("npc_wiki_metadata_loader: loaded %d cleaned NPC wiki metadata rows", len(rows))
    return rows
