"""
npc_room_resolver.py
--------------------
Resolves Lua-authored NPC templates onto local wayto room ids using the
project's room graph.

Resolution order is intentionally conservative:
    1. Exact name/title establishment match in room titles
    2. Location-hint constrained role/title match

If a template cannot be matched cleanly, it is left unresolved.
"""

from __future__ import annotations

import logging
import os
import re
from collections import defaultdict

from server.core.scripting.loaders.npc_placement_alias_loader import load_npc_placement_aliases
from server.core.scripting.loaders.npc_wiki_metadata_loader import load_npc_wiki_metadata

log = logging.getLogger(__name__)

def _normalize_hint_key(text: str) -> str:
    text = str(text or "").lower()
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

_HINT_ALIASES = {
    _normalize_hint_key("kharam-dzu"): ("kharam", "dzu"),
    _normalize_hint_key("wehnimer's landing"): ("wehnimers", "landing"),
    _normalize_hint_key("wehnimer's landing area"): ("wehnimers", "landing"),
    _normalize_hint_key("wehnimer's landing bay"): ("wehnimers", "bay"),
    _normalize_hint_key("ta'illistim"): ("taillistim",),
    _normalize_hint_key("ta'illistim area"): ("taillistim",),
    _normalize_hint_key("ta'illistim court"): ("taillistim", "court"),
    _normalize_hint_key("ta'vaalor"): ("tavaalor",),
    _normalize_hint_key("zul logoth"): ("zul", "logoth"),
    _normalize_hint_key("mist harbor"): ("mist", "harbor"),
    _normalize_hint_key("icemule trace"): ("icemule", "trace"),
    _normalize_hint_key("river's rest"): ("rivers", "rest"),
    _normalize_hint_key("river's rest coastal area"): ("rivers", "rest", "coastal"),
    _normalize_hint_key("kraken's fall"): ("krakens", "fall"),
    _normalize_hint_key("old ta'faendryl"): ("old", "tafaendryl"),
    _normalize_hint_key("open sea"): ("sea",),
}

_TITLE_STOPWORDS = {
    "a", "an", "the", "and", "of", "for", "to", "in", "on", "at",
    "area", "town", "city", "village", "court", "road", "way", "lane",
    "shop", "store", "merchant", "man", "woman", "human", "elven", "elf",
    "dwarven", "dwarf", "halfling", "gnome", "pirate", "noble", "courtier",
    "soldier", "guard", "guardsman", "sentry", "scholar", "artisan", "smith",
    "weaponsmith", "merchant", "mystic", "seafarer", "bartender", "baker",
    "priest", "healer", "innkeeper", "teller", "clerk", "taskmaster",
}

_ROLE_KEYWORDS = {
    "bartender": {"tavern", "spirits", "ale", "pub", "bar", "taproom", "inn"},
    "baker": {"bakery", "bakehouse", "bread", "oven"},
    "smith": {"forge", "smithy", "weaponry", "armory", "armoury", "anvil"},
    "weaponsmith": {"forge", "smithy", "weaponry", "armory", "armoury"},
    "merchant": {"market", "shop", "store", "bazaar", "emporium"},
    "seafarer": {"docks", "dock", "harbor", "harbour", "sea", "ship", "wharf"},
    "innkeeper": {"inn", "hostel", "lodge", "tavern"},
    "teller": {"bank", "exchange", "counting", "vault"},
    "priest": {"temple", "shrine", "sanctuary"},
}

_WIKI_AREA_SKIP = {
    "wandering",
    "town",
    "alternate reality/blood world",
    "blood world",
    "open sea",
    "festivals",
    "premium festival",
    "ebon gate",
    "mercantile guild",
}

_AREA_HUB_WORDS = (
    ("town center", 90),
    ("square", 80),
    ("market", 75),
    ("promenade", 70),
    ("landing", 68),
    ("inner ring", 65),
    ("outer circle", 60),
    ("courtyard", 55),
    ("entrance", 50),
    ("atrium", 45),
    ("gate", 40),
    ("center", 35),
)

_PRIVATE_AREA_WORDS = (
    "hall", "manor", "guild", "estate", "villa", "hotel", "monastery",
    "academy", "temple", "library", "cottage", "shack", "shop", "boutique",
    "showroom", "sales room", "wagon", "inn",
)

_DIRECTIONAL_ROOM_SUFFIXES = (
    " north", " south", " east", " west", " northeast", " northwest",
    " southeast", " southwest", " ne", " nw", " se", " sw",
)

_SHOP_PUBLIC_ROOM_WORDS = (
    ("entry", 45),
    ("foyer", 40),
    ("lobby", 38),
    ("reception", 34),
    ("front", 30),
    ("showroom", 30),
    ("sales room", 30),
    ("boutique", 28),
    ("counter", 28),
    ("landing", 22),
    ("atrium", 20),
    ("lounge", 14),
)

_SHOP_BACKROOM_WORDS = (
    "basement", "undercroft", "workshop", "office", "study", "storage",
    "backroom", "treatment", "triage", "laboratory", "cognition", "chance",
    "tricks", "lounge", "the room", "west room",
)

_AFFILIATION_SEGMENT_SKIP = {
    "unknown", "himself", "wandering caravan", "mysterious client",
    "dark alliance", "the resistance",
}

_AFFILIATION_PUBLIC_ROOM_WORDS = (
    ("entry court", 42),
    ("front room", 40),
    ("entry way", 39),
    ("entry", 40),
    ("entrance", 38),
    ("foyer", 36),
    ("lobby", 34),
    ("atrium", 32),
    ("courtyard", 30),
    ("plaza", 28),
    ("gates", 28),
    ("entry court", 30),
    ("gateway", 28),
    ("rotunda", 26),
    ("gate", 26),
    ("temple", 24),
    ("chapel", 24),
    ("arena", 24),
    ("narthex", 22),
    ("vestibule", 20),
    ("sanctuary", 18),
    ("nave", 18),
    ("front lawn", 18),
    ("hall", 14),
)

_AFFILIATION_REJECT_TITLE_WORDS = (
    "table",
    "room",
)

_FAMILY_SURNAME_SKIP = {
    "artisan",
    "captain",
    "clerk",
    "courtier",
    "elf",
    "engineer",
    "healer",
    "host",
    "hunter",
    "lawyer",
    "magister",
    "man",
    "merchant",
    "noble",
    "officer",
    "pirate",
    "scholar",
    "seamstress",
    "smith",
    "soldier",
    "sorcerer",
    "warlord",
    "wizard",
    "woman",
}


def _normalize_text(text: str) -> str:
    text = str(text or "").lower()
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_title_key(text: str) -> str:
    value = str(text or "").strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return _normalize_text(value)


def _normalize_room_tag(text: str) -> str:
    return _normalize_text(text).replace(" ", ":")


def _tokenize(text: str) -> tuple[str, ...]:
    normalized = _normalize_text(text)
    if not normalized:
        return ()
    return tuple(token for token in normalized.split(" ") if token)


def _expand_title_tokens(tokens) -> set[str]:
    expanded = set()
    for token in tokens or ():
        token = str(token or "").strip()
        if not token:
            continue
        expanded.add(token)
        if token.endswith("s") and len(token) > 4:
            expanded.add(token[:-1])
    return expanded


def _sql_unescape(text: str) -> str:
    value = str(text or "")
    value = value.replace("\\'", "'")
    value = value.replace('\\"', '"')
    value = value.replace("\\\\", "\\")
    return value


def _location_tokens(hint: str) -> tuple[str, ...]:
    normalized = _normalize_text(hint)
    if not normalized:
        return ()
    return _HINT_ALIASES.get(normalized, _tokenize(normalized))


def _distinctive_name_tokens(name: str, title: str) -> list[str]:
    preferred = []
    seen = set()
    for token in list(_tokenize(name)) + list(_tokenize(title)):
        if len(token) < 4 or token in _TITLE_STOPWORDS or token in seen:
            continue
        seen.add(token)
        preferred.append(token)
    return preferred


def _load_room_index(scripts_path: str) -> dict:
    project_root = os.path.abspath(os.path.join(scripts_path, ".."))
    room_graph_path = os.path.join(project_root, "client", "data", "room_graph.json")
    if not os.path.isfile(room_graph_path):
        log.warning("npc_room_resolver: room graph not found at %s", room_graph_path)
        return []

    rooms_by_id = {}
    title_index = defaultdict(set)
    exact_title_index = defaultdict(set)
    area_index = defaultdict(set)
    try:
        with open(room_graph_path, "r", encoding="utf-8-sig") as handle:
            in_rooms = False
            brace_depth = 0
            current = None
            for raw_line in handle:
                line = raw_line.rstrip("\r\n")
                stripped = line.strip()
                if not in_rooms:
                    if stripped.startswith('"rooms"') or stripped.startswith('"rooms":'):
                        in_rooms = True
                    continue

                if current is None:
                    match = re.match(r'^\s*"(\d+)":\s*\{\s*$', line)
                    if match:
                        current = {
                            "room_id": int(match.group(1)),
                            "title": "",
                            "zone_name": "",
                            "location": "",
                            "region_name": "",
                            "image": "",
                            "tags": [],
                        }
                        brace_depth = 1
                        in_tags = False
                    elif stripped == "}":
                        break
                    continue

                brace_depth += line.count("{")
                brace_depth -= line.count("}")

                if in_tags:
                    for item in re.findall(r'"([^"]+)"', line):
                        value = str(item or "").strip()
                        if value:
                            current["tags"].append(value)
                    if "]" in line:
                        in_tags = False
                    if brace_depth <= 0:
                        in_tags = False

                for key in ("title", "zone_name", "location", "region_name", "image"):
                    match = re.match(rf'^\s*"{key}":\s*"(.*)"[,]?\s*$', line)
                    if match:
                        current[key] = match.group(1)
                        break
                else:
                    if re.match(r'^\s*"tags":\s*\[', line):
                        in_tags = True
                        for item in re.findall(r'"([^"]+)"', line):
                            if item != "tags":
                                current["tags"].append(str(item).strip())
                        if "]" in line:
                            in_tags = False

                if brace_depth <= 0:
                    title = str(current.get("title") or "")
                    zone_name = str(current.get("zone_name") or "")
                    location = str(current.get("location") or "")
                    region_name = str(current.get("region_name") or "")
                    image = str(current.get("image") or "")
                    raw_tags = list(current.get("tags") or [])
                    # Map asset slugs can contain neighboring town names and pollute
                    # authoritative location-hint matches, so area tokens stay limited
                    # to human-readable room metadata.
                    area_text = " | ".join(part for part in (title, zone_name, location) if part)
                    room_id = int(current["room_id"])
                    title_tokens = _expand_title_tokens(_tokenize(title))
                    tag_values = set()
                    for raw_tag in raw_tags:
                        tag_norm = _normalize_room_tag(raw_tag)
                        if not tag_norm:
                            continue
                        tag_values.add(tag_norm)
                        if ":" in tag_norm:
                            tag_values.add(tag_norm.split(":")[-1])
                    room_data = {
                        "room_id": room_id,
                        "title": title,
                        "title_label": str(title).strip()[1:-1] if str(title).startswith("[") and str(title).endswith("]") else str(title),
                        "title_norm": _normalize_text(title),
                        "zone_norm": _normalize_text(zone_name),
                        "location_norm": _normalize_text(location),
                        "region_norm": _normalize_text(region_name),
                        "title_tokens": title_tokens,
                        "area_tokens": set(_tokenize(area_text)),
                        "tag_values": tag_values,
                    }
                    rooms_by_id[room_id] = room_data
                    exact_title = _normalize_title_key(title)
                    if exact_title:
                        exact_title_index[exact_title].add(room_id)
                    for token in room_data["title_tokens"]:
                        title_index[token].add(room_id)
                    for token in room_data["area_tokens"]:
                        area_index[token].add(room_id)
                    current = None
                    brace_depth = 0
    except Exception as exc:
        log.error("npc_room_resolver: failed scanning %s (%s)", room_graph_path, exc, exc_info=True)
        return {"rooms_by_id": {}, "title_index": {}, "area_index": {}}

    return {
        "rooms_by_id": rooms_by_id,
        "title_index": dict(title_index),
        "exact_title_index": dict(exact_title_index),
        "area_index": dict(area_index),
    }


def _hint_matches_room(location_hint: str, room: dict) -> bool:
    tokens = _location_tokens(location_hint)
    if not tokens:
        return True
    area_tokens = room.get("area_tokens") or set()
    return all(token in area_tokens for token in tokens)


def _union_room_ids(index: dict, tokens) -> set[int]:
    out = set()
    for token in tokens or ():
        out.update(index.get(token, set()) or set())
    return out


def _intersect_room_ids(index: dict, tokens) -> set[int]:
    groups = [set(index.get(token, set()) or set()) for token in (tokens or ()) if index.get(token)]
    if not groups:
        return set()
    groups.sort(key=len)
    out = set(groups[0])
    for group in groups[1:]:
        out &= group
        if not out:
            break
    return out


def _role_keywords(template: dict) -> set[str]:
    role_words = set()
    name = _normalize_text(template.get("name") or "")
    title = _normalize_text(template.get("title") or "")
    for source in (name, title):
        for word in source.split(" "):
            if word in _ROLE_KEYWORDS:
                role_words.update(_ROLE_KEYWORDS[word])
    return role_words


def _metadata_area_groups(metadata: dict) -> list[tuple[str, ...]]:
    groups = []
    seen = set()
    for raw in [metadata.get("hometown")] + list(metadata.get("venues") or []):
        value = str(raw or "").strip()
        if not value:
            continue
        if _normalize_text(value) in _WIKI_AREA_SKIP:
            continue
        tokens = _location_tokens(value)
        if not tokens:
            continue
        key = tuple(tokens)
        if key in seen:
            continue
        seen.add(key)
        groups.append(key)
    return groups


def _metadata_matches_room(metadata: dict, room: dict) -> bool:
    area_groups = _metadata_area_groups(metadata)
    if not area_groups:
        return True
    area_tokens = set(room.get("area_tokens") or set())
    return any(all(token in area_tokens for token in group) for group in area_groups)


def _shop_name_variants(shop_name: str) -> list[str]:
    variants = []
    base = _normalize_title_key(shop_name)
    if not base:
        return variants
    variants.append(base)
    for article in ("the ", "a ", "an "):
        if base.startswith(article):
            trimmed = base[len(article):].strip()
            if trimmed:
                variants.append(trimmed)
        else:
            variants.append(f"{article}{base}")
    out = []
    seen = set()
    for variant in variants:
        norm = _normalize_text(variant)
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out


def _iter_metadata_area_values(metadata: dict):
    seen = set()
    for raw in list(metadata.get("venues") or []) + [metadata.get("hometown")]:
        value = str(raw or "").strip()
        norm = _normalize_text(value)
        if not value or not norm or norm in _WIKI_AREA_SKIP or norm in seen:
            continue
        seen.add(norm)
        yield value, norm


def _affiliation_segments(affiliation: str, hometown: str = "") -> list[str]:
    text = str(affiliation or "").strip()
    if not text:
        return []
    text = text.replace("|", " ").replace("#", " ")
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<!^)(?=(?:House of |Order of |Temple of |Church of |Hall of ))", "|", text)
    text = re.sub(r"(?<!^)(?=(?:[A-Z][A-Za-z' -]+ family of ))", "|", text)
    hometown_norm = _normalize_text(hometown)
    segments = []
    seen = set()
    for raw in re.split(r"[;,/|]| previously\.| and ", text, flags=re.IGNORECASE):
        value = str(raw or "").strip()
        norm = _normalize_text(value)
        if not norm or norm in seen or norm in _AFFILIATION_SEGMENT_SKIP:
            continue
        if hometown_norm and norm == hometown_norm:
            continue
        tokens = [token for token in norm.split(" ") if token]
        if len(tokens) > 8 or len(value) > 64:
            continue
        if len(tokens) >= 2 or (len(tokens) == 1 and len(tokens[0]) >= 5):
            segments.append(value)
            seen.add(norm)
    return segments


def _affiliation_segment_variants(segment: str, alias_map: dict[str, list[str]] | None = None) -> list[str]:
    variants = []
    value = str(segment or "").strip()
    if not value:
        return variants
    variants.append(value)
    alias_values = []
    if alias_map:
        alias_values = list(alias_map.get(value, []) or [])
        if not alias_values:
            segment_norm = _normalize_text(value)
            for key, mapped in (alias_map or {}).items():
                if _normalize_text(key) == segment_norm:
                    alias_values = list(mapped or [])
                    break
    for alias in alias_values:
        if alias:
            variants.append(str(alias).strip())
    normalized = _normalize_text(value)
    match = re.match(r"^church of (.+)$", normalized)
    if match:
        deity = match.group(1).strip()
        if deity:
            variants.append(f"Temple of {deity.title()}")
            variants.append(f"{deity.title()}'s Temple")
    match = re.match(r"^temple of (.+)$", normalized)
    if match:
        deity = match.group(1).strip()
        if deity:
            variants.append(f"{deity.title()}'s Temple")
    match = re.match(r"^house of (.+)$", normalized)
    if match:
        house_name = match.group(1).strip().title()
        if house_name:
            for suffix in ("Plaza", "Way", "Court", "Manor", "Hall", "Estate", "House", "Inn", "Gardens"):
                variants.append(f"{house_name} {suffix}")
    match = re.match(r"^(.+?) family of .+$", normalized)
    if match:
        family_name = match.group(1).strip().title()
        if family_name:
            for suffix in ("Manor", "Plaza", "Way", "Court", "Hall", "Inn", "Estate", "House", "Gardens"):
                variants.append(f"{family_name} {suffix}")
    if normalized.endswith(" consortium"):
        variants.append("Consortium")
    if normalized.endswith(" school"):
        variants.append("Schoolhouse")
    if normalized.endswith(" hotel"):
        variants.append("The Hotel")
    out = []
    seen = set()
    for item in variants:
        norm = _normalize_text(item)
        if norm and norm not in seen:
            seen.add(norm)
            out.append(item)
    return out


def _affiliation_title_matches(segment_norm: str, room: dict) -> bool:
    title_norm = str(room.get("title_norm") or "")
    if not title_norm or not segment_norm:
        return False
    if (
        title_norm == segment_norm
        or title_norm.startswith(f"{segment_norm} ")
        or title_norm.startswith(f"{segment_norm},")
        or segment_norm in title_norm
    ):
        return True
    segment_tokens = [token for token in segment_norm.split(" ") if token]
    if len(segment_tokens) == 1 and len(segment_tokens[0]) >= 5:
        stem = segment_tokens[0]
        for title_token in room.get("title_tokens") or set():
            if str(title_token).startswith(stem) and len(str(title_token)) <= len(stem) + 3:
                return True
    return False


def _lookup_affiliation_values(mapping: dict[str, list[str]] | None, key: str) -> list[str]:
    if not mapping:
        return []
    key = str(key or "").strip()
    if not key:
        return []
    values = list((mapping or {}).get(key, []) or [])
    if values:
        return values
    key_norm = _normalize_text(key)
    for raw_key, raw_values in (mapping or {}).items():
        if _normalize_text(raw_key) == key_norm:
            return list(raw_values or [])
    return []


def _room_public_bonus(title_norm: str) -> int:
    score = 0
    for word, points in _AFFILIATION_PUBLIC_ROOM_WORDS:
        if word in title_norm:
            score += points
    if any(word in title_norm for word in _SHOP_BACKROOM_WORDS):
        score -= 25
    if any(title_norm.endswith(suffix) for suffix in _DIRECTIONAL_ROOM_SUFFIXES):
        score -= 10
    return score


def _family_name_tokens(name: str) -> tuple[str, ...]:
    parts = re.findall(r"[A-Za-z][A-Za-z'\-]+", str(name or ""))
    if len(parts) < 2:
        return ()
    out: list[str] = []
    seen: set[str] = set()
    for raw_token in parts[1:]:
        token = _normalize_text(raw_token)
        if not token or len(token) < 4 or token in _FAMILY_SURNAME_SKIP or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return tuple(out)


def _candidate_template_ids_for_tokens(token_map: dict[str, set[str]], tokens: set[str]) -> set[str]:
    out = set()
    for token in tokens or ():
        out.update(token_map.get(token, set()) or set())
    return out


def _score_room(template: dict, room: dict) -> int:
    score = 0
    title_norm = str(room.get("title_norm") or "")
    title_tokens = set(room.get("title_tokens") or set())
    location_hint = str(template.get("location_hint") or "")
    name = str(template.get("name") or "")
    full_name = _normalize_text(name)
    distinct_tokens = _distinctive_name_tokens(name, str(template.get("title") or ""))
    role_words = _role_keywords(template)

    if full_name and full_name in title_norm:
        score += 120

    possessive_hits = 0
    token_hits = 0
    for token in distinct_tokens:
        if f"{token}s " in title_norm or f"{token}s]" in title_norm:
            possessive_hits += 1
        elif token in title_tokens:
            token_hits += 1
    if possessive_hits:
        score += 95 + (possessive_hits * 5)
    elif len(distinct_tokens) >= 2 and token_hits >= 2:
        score += 70 + (token_hits * 5)
    elif token_hits == 1:
        score += 45

    if role_words and any(word in title_tokens for word in role_words):
        score += 20

    if location_hint and _hint_matches_room(location_hint, room):
        score += 15

    comma_penalty = str(room.get("title") or "").count(",") * 10
    score -= comma_penalty
    return score


def resolve_npc_home_rooms(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    title_index = dict(room_index.get("title_index") or {})
    area_index = dict(room_index.get("area_index") or {})
    if not rooms_by_id:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        distinct_tokens = _distinctive_name_tokens(
            str(template.get("name") or ""),
            str(template.get("title") or ""),
        )
        role_words = _role_keywords(template)
        hint_tokens = _location_tokens(str(template.get("location_hint") or ""))

        hint_room_ids = _intersect_room_ids(area_index, hint_tokens) if hint_tokens else set()
        candidate_ids = _union_room_ids(title_index, distinct_tokens)
        if not candidate_ids and role_words:
            role_candidates = _union_room_ids(title_index, role_words)
            if hint_room_ids:
                candidate_ids = role_candidates & hint_room_ids
            else:
                candidate_ids = role_candidates

        if not candidate_ids:
            continue

        scored = []
        for room_id in candidate_ids:
            room = rooms_by_id.get(int(room_id))
            if not room:
                continue
            score = _score_room(template, room)
            if score < 60:
                continue
            scored.append((score, int(room["room_id"])))
        if not scored:
            continue

        scored.sort(key=lambda row: (-row[0], row[1]))
        best_score, best_room = scored[0]
        next_score = scored[1][0] if len(scored) > 1 else -999
        if best_score < 80:
            continue
        if next_score >= best_score - 5:
            continue
        resolved[str(template_id)] = int(best_room)

    log.info("npc_room_resolver: resolved %d NPC home rooms from local room graph", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_sql_dump(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    project_root = os.path.abspath(os.path.join(scripts_path, ".."))
    dump_path = os.path.join(project_root, "USETHIS.sql")
    if not os.path.isfile(dump_path):
        return {}
    metadata_rows = load_npc_wiki_metadata(scripts_path)

    unresolved = {}
    token_map: dict[str, set[str]] = defaultdict(set)
    meta = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue
        distinct_tokens = _distinctive_name_tokens(
            str(template.get("name") or ""),
            str(template.get("title") or ""),
        )
        if not distinct_tokens:
            continue
        unresolved[str(template_id)] = template
        meta[str(template_id)] = {
            "full_name": _normalize_text(str(template.get("name") or "")),
            "location_hint": str(template.get("location_hint") or ""),
            "distinct_tokens": distinct_tokens,
            "role_words": _role_keywords(template),
            "wiki_metadata": metadata_rows.get(str(template_id)) or {},
        }
        for token in distinct_tokens:
            token_map[token].add(str(template_id))

    if not unresolved:
        return {}

    room_pattern = re.compile(
        r"^\((\d+),\d+,'((?:\\'|[^'])*)','((?:\\'|[^'])*)',\d+,'((?:\\'|[^'])*)','((?:\\'|[^'])*)',"
    )
    best: dict[str, tuple[int, int]] = {}
    second: dict[str, int] = {}

    try:
        with open(dump_path, "r", encoding="utf-8", errors="ignore") as handle:
            for raw_line in handle:
                if not raw_line.startswith("("):
                    continue
                match = room_pattern.match(raw_line)
                if not match:
                    continue
                room_id = int(match.group(1))
                title = _sql_unescape(match.group(2))
                description = _sql_unescape(match.group(3))
                location = _sql_unescape(match.group(5))
                content_text = " | ".join(part for part in (title, description, location) if part)
                content_norm = _normalize_text(content_text)
                content_tokens = _expand_title_tokens(_tokenize(content_text))
                if not content_tokens:
                    continue

                for template_id in _candidate_template_ids_for_tokens(token_map, content_tokens):
                    template = unresolved.get(template_id)
                    if not template:
                        continue
                    entry = meta[template_id]
                    score = 0

                    if entry["full_name"] and entry["full_name"] in content_norm:
                        score += 150

                    token_hits = sum(1 for token in entry["distinct_tokens"] if token in content_tokens)
                    if token_hits == len(entry["distinct_tokens"]) and token_hits >= 2:
                        score += 85 + (token_hits * 5)
                    elif token_hits == 1:
                        score += 45

                    title_norm = _normalize_text(title)
                    for token in entry["distinct_tokens"]:
                        if token and f"{token}s " in title_norm or token and f"{token}s]" in title_norm:
                            score += 35
                            break

                    if entry["role_words"] and any(word in content_tokens for word in entry["role_words"]):
                        score += 20

                    hint_room = {
                        "area_tokens": set(_tokenize(location + " | " + title)),
                    }
                    if entry["location_hint"] and _hint_matches_room(entry["location_hint"], hint_room):
                        score += 15
                    if _metadata_matches_room(entry["wiki_metadata"], hint_room):
                        score += 25

                    if score < 95:
                        continue

                    current_best = best.get(template_id)
                    if not current_best or score > current_best[0]:
                        if current_best:
                            second[template_id] = max(second.get(template_id, -999), current_best[0])
                        best[template_id] = (score, room_id)
                    elif room_id != current_best[1]:
                        second[template_id] = max(second.get(template_id, -999), score)
    except Exception as exc:
        log.error("npc_room_resolver: failed scanning SQL dump %s (%s)", dump_path, exc, exc_info=True)
        return {}

    resolved = {}
    for template_id, (score, room_id) in best.items():
        runner_up = second.get(template_id, -999)
        if score >= 110 and runner_up <= score - 8:
            resolved[template_id] = int(room_id)

    log.info("npc_room_resolver: resolved %d NPC home rooms from SQL dump references", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_sql_exact_names(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    project_root = os.path.abspath(os.path.join(scripts_path, ".."))
    dump_path = os.path.join(project_root, "USETHIS.sql")
    if not os.path.isfile(dump_path):
        return {}
    metadata_rows = load_npc_wiki_metadata(scripts_path)

    unresolved = {}
    token_map: dict[str, set[str]] = defaultdict(set)
    meta = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue
        full_name = _normalize_text(str(template.get("name") or ""))
        distinct_tokens = _distinctive_name_tokens(
            str(template.get("name") or ""),
            str(template.get("title") or ""),
        )
        if not full_name or len(full_name) < 5 or not distinct_tokens:
            continue
        unresolved[str(template_id)] = template
        meta[str(template_id)] = {
            "full_name": full_name,
            "location_hint": str(template.get("location_hint") or ""),
            "distinct_tokens": distinct_tokens,
            "role_words": _role_keywords(template),
            "wiki_metadata": metadata_rows.get(str(template_id)) or {},
        }
        for token in distinct_tokens:
            token_map[token].add(str(template_id))

    if not unresolved:
        return {}

    room_pattern = re.compile(
        r"^\((\d+),\d+,'((?:\\'|[^'])*)','((?:\\'|[^'])*)',\d+,'((?:\\'|[^'])*)','((?:\\'|[^'])*)',"
    )
    best: dict[str, tuple[int, int, str]] = {}
    second: dict[str, int] = {}

    try:
        with open(dump_path, "r", encoding="utf-8", errors="ignore") as handle:
            for raw_line in handle:
                if not raw_line.startswith("("):
                    continue
                match = room_pattern.match(raw_line)
                if not match:
                    continue
                room_id = int(match.group(1))
                title = _sql_unescape(match.group(2))
                description = _sql_unescape(match.group(3))
                location = _sql_unescape(match.group(5))
                content_text = " | ".join(part for part in (title, description, location) if part)
                content_norm = _normalize_text(content_text)
                content_tokens = _expand_title_tokens(_tokenize(content_text))
                if not content_tokens:
                    continue

                hint_room = {
                    "area_tokens": set(_tokenize(location + " | " + title)),
                }
                title_norm = _normalize_text(title)
                for template_id in _candidate_template_ids_for_tokens(token_map, content_tokens):
                    entry = meta.get(template_id)
                    if not entry:
                        continue
                    if entry["full_name"] not in content_norm:
                        continue

                    score = 220
                    if entry["full_name"] in title_norm:
                        score += 35
                    if entry["location_hint"] and _hint_matches_room(entry["location_hint"], hint_room):
                        score += 15
                    if _metadata_matches_room(entry["wiki_metadata"], hint_room):
                        score += 25
                    if entry["role_words"] and any(word in content_tokens for word in entry["role_words"]):
                        score += 10

                    current_best = best.get(template_id)
                    candidate = (score, room_id, title_norm)
                    if not current_best or score > current_best[0]:
                        if current_best and current_best[2] != candidate[2]:
                            second[template_id] = max(second.get(template_id, -999), current_best[0])
                        best[template_id] = candidate
                    elif current_best[2] != candidate[2]:
                        second[template_id] = max(second.get(template_id, -999), score)
    except Exception as exc:
        log.error("npc_room_resolver: failed scanning SQL dump %s for exact names (%s)", dump_path, exc, exc_info=True)
        return {}

    resolved = {}
    for template_id, (score, room_id, _title_norm) in best.items():
        runner_up = second.get(template_id, -999)
        if score >= 220 and runner_up <= score - 12:
            resolved[template_id] = int(room_id)

    log.info("npc_room_resolver: resolved %d NPC home rooms from exact SQL name mentions", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_template_titles(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    placement_aliases = load_npc_placement_aliases(scripts_path)
    template_room_titles = dict((placement_aliases or {}).get("template_room_titles") or {})
    if not template_room_titles:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    exact_title_index = dict(room_index.get("exact_title_index") or {})
    if not rooms_by_id or not exact_title_index:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        title_aliases = list(template_room_titles.get(str(template_id)) or [])
        if not title_aliases:
            continue
        location_hint = str(template.get("location_hint") or "").strip()

        best = None
        runner_up = -999
        for title_alias in title_aliases:
            title_norm = _normalize_title_key(title_alias)
            if not title_norm:
                continue
            for room_id in exact_title_index.get(title_norm, set()) or set():
                room = rooms_by_id.get(int(room_id))
                if not room:
                    continue
                if location_hint and not _hint_matches_room(location_hint, room):
                    continue
                room_title_norm = str(room.get("title_norm") or "")
                score = 280 + _room_public_bonus(room_title_norm)
                candidate = (score, int(room["room_id"]), room_title_norm)
                if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                    if best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 2:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from template-specific room titles", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_template_title_overrides(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    placement_aliases = load_npc_placement_aliases(scripts_path)
    template_room_titles = dict((placement_aliases or {}).get("template_room_titles_override_hint") or {})
    if not template_room_titles:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    exact_title_index = dict(room_index.get("exact_title_index") or {})
    if not rooms_by_id or not exact_title_index:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        title_aliases = list(template_room_titles.get(str(template_id)) or [])
        if not title_aliases:
            continue

        best = None
        runner_up = -999
        for title_alias in title_aliases:
            title_norm = _normalize_title_key(title_alias)
            if not title_norm:
                continue
            for room_id in exact_title_index.get(title_norm, set()) or set():
                room = rooms_by_id.get(int(room_id))
                if not room:
                    continue
                room_title_norm = str(room.get("title_norm") or "")
                score = 320 + _room_public_bonus(room_title_norm)
                candidate = (score, int(room["room_id"]), room_title_norm)
                if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                    if best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 2:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from override room titles", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_location_hint_titles(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    placement_aliases = load_npc_placement_aliases(scripts_path)
    hint_room_titles = dict((placement_aliases or {}).get("location_hint_room_titles") or {})
    if not hint_room_titles:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    exact_title_index = dict(room_index.get("exact_title_index") or {})
    if not rooms_by_id or not exact_title_index:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        location_hint = str(template.get("location_hint") or "").strip()
        if not location_hint:
            continue
        title_aliases = list(hint_room_titles.get(location_hint) or [])
        if not title_aliases:
            continue

        best = None
        runner_up = -999
        for title_alias in title_aliases:
            title_norm = _normalize_title_key(title_alias)
            if not title_norm:
                continue
            for room_id in exact_title_index.get(title_norm, set()) or set():
                room = rooms_by_id.get(int(room_id))
                if not room:
                    continue
                room_title_norm = str(room.get("title_norm") or "")
                score = 210 + _room_public_bonus(room_title_norm)
                candidate = (score, int(room["room_id"]), room_title_norm)
                if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                    if best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 2:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from location-hint hub titles", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_template_prefixes(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    placement_aliases = load_npc_placement_aliases(scripts_path)
    template_room_prefixes = dict((placement_aliases or {}).get("template_room_prefixes") or {})
    if not template_room_prefixes:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        prefix_aliases = list(template_room_prefixes.get(str(template_id)) or [])
        if not prefix_aliases:
            continue
        location_hint = str(template.get("location_hint") or "").strip()

        best = None
        runner_up = -999
        for prefix_alias in prefix_aliases:
            prefix_norm = _normalize_title_key(prefix_alias)
            if not prefix_norm:
                continue
            for room in rooms_by_id.values():
                room_title_norm = str(room.get("title_norm") or "")
                if not room_title_norm:
                    continue
                if room_title_norm != prefix_norm and not room_title_norm.startswith(f"{prefix_norm},") and not room_title_norm.startswith(f"{prefix_norm} "):
                    continue
                if location_hint and not _hint_matches_room(location_hint, room):
                    continue

                score = 250 + _room_public_bonus(room_title_norm)
                if room_title_norm == prefix_norm:
                    score += 20
                elif room_title_norm.startswith(f"{prefix_norm},"):
                    score += 10
                candidate = (score, int(room["room_id"]), room_title_norm)
                if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                    if best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 2:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from template-specific room prefixes", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_role_tags(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    placement_aliases = load_npc_placement_aliases(scripts_path)
    role_room_tags = dict((placement_aliases or {}).get("role_room_tags") or {})
    if not role_room_tags:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        role = _normalize_text(template.get("title") or "")
        role_tag_values = {
            _normalize_room_tag(value)
            for value in list(role_room_tags.get(role) or [])
            if str(value or "").strip()
        }
        if not role_tag_values:
            continue

        location_hint = str(template.get("location_hint") or "").strip()
        best = None
        runner_up = -999
        for room in rooms_by_id.values():
            title_norm = str(room.get("title_norm") or "")
            if not title_norm:
                continue
            if location_hint and not _hint_matches_room(location_hint, room):
                continue

            tag_values = set(room.get("tag_values") or set())
            if not any(tag_value in tag_values for tag_value in role_tag_values):
                continue

            score = 250 + _room_public_bonus(title_norm)
            candidate = (score, int(room["room_id"]), title_norm)
            if best is None or candidate[0] > best[0]:
                if best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, best[0])
                best = candidate
            elif best is not None and best[2] != candidate[2]:
                runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 10:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from role-tagged service shops", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_registry_family_clusters(
    templates: dict[str, dict],
    registry_rows: dict[str, dict],
    scripts_path: str,
) -> dict[str, int]:
    if not registry_rows:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    peer_rooms: dict[tuple[str, str], set[int]] = defaultdict(set)
    peer_counts: dict[tuple[str, str], int] = defaultdict(int)

    for template_id, row in sorted((registry_rows or {}).items()):
        try:
            room_id = int(row.get("home_room_id") or 0)
        except (TypeError, ValueError):
            room_id = 0
        if room_id <= 0:
            continue

        room = rooms_by_id.get(room_id)
        if not room:
            continue

        template = dict((templates or {}).get(str(template_id)) or {})
        display_name = str(row.get("display_name") or template.get("name") or "").strip()
        family_tokens = _family_name_tokens(display_name)
        if not family_tokens:
            continue

        location_hint = str(row.get("location_hint") or template.get("location_hint") or "").strip()
        if not location_hint or not _hint_matches_room(location_hint, room):
            continue

        hint_key = _normalize_text(location_hint)
        for family_token in family_tokens:
            key = (family_token, hint_key)
            peer_rooms[key].add(int(room_id))
            peer_counts[key] += 1

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        location_hint = str(template.get("location_hint") or "").strip()
        if not location_hint:
            continue

        family_tokens = _family_name_tokens(str(template.get("name") or ""))
        if not family_tokens:
            continue

        candidate_rooms: set[int] = set()
        evidence = 0
        hint_key = _normalize_text(location_hint)
        for family_token in family_tokens:
            key = (family_token, hint_key)
            family_room_ids = set(peer_rooms.get(key) or set())
            if len(family_room_ids) != 1:
                continue
            candidate_rooms.update(family_room_ids)
            evidence += int(peer_counts.get(key, 0) or 0)

        if len(candidate_rooms) != 1 or evidence <= 0:
            continue

        resolved[str(template_id)] = int(next(iter(candidate_rooms)))

    log.info("npc_room_resolver: resolved %d NPC home rooms from registry family clusters", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_registry_affiliation_clusters(
    templates: dict[str, dict],
    registry_rows: dict[str, dict],
    scripts_path: str,
) -> dict[str, int]:
    if not registry_rows:
        return {}

    metadata_rows = load_npc_wiki_metadata(scripts_path)
    if not metadata_rows:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    peer_rooms: dict[str, set[int]] = defaultdict(set)
    peer_counts: dict[str, int] = defaultdict(int)
    peer_hints: dict[str, set[str]] = defaultdict(set)

    for template_id, row in sorted((registry_rows or {}).items()):
        metadata = metadata_rows.get(str(template_id)) or {}
        affiliation = str(metadata.get("affiliation") or "").strip()
        if not affiliation:
            continue
        try:
            room_id = int(row.get("home_room_id") or 0)
        except (TypeError, ValueError):
            room_id = 0
        if room_id <= 0:
            continue

        room = rooms_by_id.get(room_id)
        if not room:
            continue
        if any(tag_value in {"playershop", "meta:playershop"} for tag_value in set(room.get("tag_values") or set())):
            continue

        hint = str(row.get("location_hint") or (templates.get(str(template_id)) or {}).get("location_hint") or "").strip()
        if not hint and not _metadata_area_groups(metadata):
            continue

        peer_rooms[affiliation].add(int(room_id))
        peer_counts[affiliation] += 1
        if hint:
            peer_hints[affiliation].add(_normalize_text(hint))

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        metadata = metadata_rows.get(str(template_id)) or {}
        affiliation = str(metadata.get("affiliation") or "").strip()
        if not affiliation:
            continue

        candidate_rooms = sorted(peer_rooms.get(affiliation) or set())
        if len(candidate_rooms) != 1 or peer_counts.get(affiliation, 0) < 2:
            continue

        hint = str(template.get("location_hint") or "").strip()
        hint_norm = _normalize_text(hint)
        room = rooms_by_id.get(candidate_rooms[0])
        if not room:
            continue

        if hint_norm:
            if hint_norm not in peer_hints.get(affiliation, set()) and not _hint_matches_room(hint, room):
                continue

        resolved[str(template_id)] = int(candidate_rooms[0])

    log.info("npc_room_resolver: resolved %d NPC home rooms from registry affiliation clusters", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_registry_affiliation_segments(
    templates: dict[str, dict],
    registry_rows: dict[str, dict],
    scripts_path: str,
) -> dict[str, int]:
    if not registry_rows:
        return {}

    metadata_rows = load_npc_wiki_metadata(scripts_path)
    if not metadata_rows:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    peer_rooms: dict[str, set[int]] = defaultdict(set)
    peer_counts: dict[str, int] = defaultdict(int)
    peer_hints: dict[str, set[str]] = defaultdict(set)

    for template_id, row in sorted((registry_rows or {}).items()):
        metadata = metadata_rows.get(str(template_id)) or {}
        segments = _affiliation_segments(
            str(metadata.get("affiliation") or ""),
            str(metadata.get("hometown") or ""),
        )
        if not segments:
            continue
        try:
            room_id = int(row.get("home_room_id") or 0)
        except (TypeError, ValueError):
            room_id = 0
        if room_id <= 0:
            continue

        room = rooms_by_id.get(room_id)
        if not room:
            continue
        title_norm = str(room.get("title_norm") or "")
        if not title_norm:
            continue
        if any(tag_value in {"playershop", "meta:playershop"} for tag_value in set(room.get("tag_values") or set())):
            continue

        hint = str(row.get("location_hint") or (templates.get(str(template_id)) or {}).get("location_hint") or "").strip()
        hint_norm = _normalize_text(hint)
        for segment in segments:
            segment_norm = _normalize_text(segment)
            if not segment_norm or not _affiliation_title_matches(segment_norm, room):
                continue
            peer_rooms[segment_norm].add(int(room_id))
            peer_counts[segment_norm] += 1
            if hint_norm:
                peer_hints[segment_norm].add(hint_norm)

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        metadata = metadata_rows.get(str(template_id)) or {}
        segments = _affiliation_segments(
            str(metadata.get("affiliation") or ""),
            str(metadata.get("hometown") or ""),
        )
        if not segments:
            continue

        hint = str(template.get("location_hint") or "").strip()
        hint_norm = _normalize_text(hint)
        best_segment = None
        best_room = 0
        best_count = 0
        for segment in segments:
            segment_norm = _normalize_text(segment)
            candidate_rooms = sorted(peer_rooms.get(segment_norm) or set())
            if len(candidate_rooms) != 1 or peer_counts.get(segment_norm, 0) < 2:
                continue

            room = rooms_by_id.get(candidate_rooms[0])
            if not room or not _affiliation_title_matches(segment_norm, room):
                continue

            if hint_norm:
                if hint_norm not in peer_hints.get(segment_norm, set()) and not _hint_matches_room(hint, room):
                    continue

            if peer_counts[segment_norm] > best_count:
                best_segment = segment_norm
                best_room = int(candidate_rooms[0])
                best_count = peer_counts[segment_norm]

        if best_segment and best_room > 0:
            resolved[str(template_id)] = best_room

    log.info("npc_room_resolver: resolved %d NPC home rooms from registry affiliation segments", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_wiki_metadata(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    metadata_rows = load_npc_wiki_metadata(scripts_path)
    if not metadata_rows:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    exact_title_index = dict(room_index.get("exact_title_index") or {})
    if not rooms_by_id or not exact_title_index:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        metadata = metadata_rows.get(str(template_id))
        if not metadata:
            continue

        candidates: dict[int, int] = {}
        for shop_link in metadata.get("shop_links") or ():
            shop_variants = _shop_name_variants(shop_link)
            if not shop_variants:
                continue
            for shop_variant in shop_variants:
                for room_id in exact_title_index.get(shop_variant, set()) or set():
                    candidates[int(room_id)] = max(candidates.get(int(room_id), -999), 260)
                for room_id, room in rooms_by_id.items():
                    title_norm = str(room.get("title_norm") or "")
                    title_label = str(room.get("title_label") or "")
                    if title_norm in shop_variants:
                        candidates[int(room_id)] = max(candidates.get(int(room_id), -999), 260)
                        continue
                    if any(
                        title_norm.startswith(f"{variant} ")
                        or title_label.startswith(f"{shop_link},")
                        or title_label.startswith(f"{shop_link} ")
                        for variant in shop_variants
                    ):
                        room_score = 220
                        lower_title = title_norm.lower()
                        for word, points in _SHOP_PUBLIC_ROOM_WORDS:
                            if word in lower_title:
                                room_score += points
                        if any(word in lower_title for word in _SHOP_BACKROOM_WORDS):
                            room_score -= 20
                        candidates[int(room_id)] = max(candidates.get(int(room_id), -999), room_score)
        if not candidates:
            continue

        scored = []
        for room_id, base_score in candidates.items():
            room = rooms_by_id.get(int(room_id))
            if not room:
                continue
            score = int(base_score)
            if _metadata_matches_room(metadata, room):
                score += 25
            if _hint_matches_room(str(template.get("location_hint") or ""), room):
                score += 10
            if str(room.get("title") or "").count(","):
                score -= 5
            scored.append((score, int(room_id), str(room.get("title_norm") or "")))

        if not scored:
            continue

        scored.sort(key=lambda row: (-row[0], row[1]))
        best_score, best_room, best_title = scored[0]
        next_score = -999
        for score, room_id, title_norm in scored[1:]:
            if title_norm != best_title:
                next_score = score
                break
        if best_score < 200:
            continue
        if next_score >= best_score - 10:
            continue
        resolved[str(template_id)] = int(best_room)

    log.info("npc_room_resolver: resolved %d NPC home rooms from wiki shop metadata", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_wiki_areas(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    metadata_rows = load_npc_wiki_metadata(scripts_path)
    if not metadata_rows:
        return {}

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        metadata = metadata_rows.get(str(template_id))
        if not metadata:
            continue

        best = None
        runner_up = -999
        for area_value, area_norm in _iter_metadata_area_values(metadata):
            area_tokens = _location_tokens(area_value)
            if not area_tokens:
                continue

            for room in rooms_by_id.values():
                combined_norm = " ".join(
                    part for part in (
                        room.get("title_norm"),
                        room.get("zone_norm"),
                        room.get("location_norm"),
                        room.get("region_norm"),
                    )
                    if part
                )
                if not all(token in combined_norm for token in area_tokens):
                    continue

                title_label = str(room.get("title_label") or "")
                title_norm = str(room.get("title_norm") or "")
                exact_area_prefix = (
                    title_label == area_value
                    or title_label.startswith(f"{area_value},")
                    or title_label.startswith(f"{area_value} ")
                )

                score = 0
                if title_label == area_value:
                    score += 220
                elif title_label.startswith(f"{area_value},"):
                    score += 200
                elif str(room.get("zone_norm") or "") == area_norm or str(room.get("location_norm") or "") == area_norm:
                    score += 90
                elif title_norm.startswith(area_norm):
                    score += 80

                for word, points in _AREA_HUB_WORDS:
                    if word in title_norm:
                        score += points

                if any(word in title_norm for word in _PRIVATE_AREA_WORDS) and not exact_area_prefix:
                    score -= 60

                if _hint_matches_room(str(template.get("location_hint") or ""), room):
                    score += 10

                if any(title_norm.endswith(suffix) for suffix in _DIRECTIONAL_ROOM_SUFFIXES):
                    score -= 10

                score -= title_label.count(",") * 4
                if score < 140:
                    continue

                candidate = (score, int(room["room_id"]), title_norm)
                if best is None or candidate[0] > best[0]:
                    if best is not None and candidate[2] != best[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and candidate[2] != best[2]:
                    runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 10:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from wiki area hubs", len(resolved))
    return resolved


def resolve_npc_home_rooms_from_affiliations(templates: dict[str, dict], scripts_path: str) -> dict[str, int]:
    metadata_rows = load_npc_wiki_metadata(scripts_path)
    if not metadata_rows:
        return {}
    placement_aliases = load_npc_placement_aliases(scripts_path)
    affiliation_aliases = dict((placement_aliases or {}).get("affiliation_aliases") or {})
    affiliation_room_tags = dict((placement_aliases or {}).get("affiliation_room_tags") or {})
    affiliation_room_titles = dict((placement_aliases or {}).get("affiliation_room_titles") or {})

    room_index = _load_room_index(scripts_path)
    rooms_by_id = dict(room_index.get("rooms_by_id") or {})
    if not rooms_by_id:
        return {}

    resolved: dict[str, int] = {}
    for template_id, template in sorted((templates or {}).items()):
        try:
            current_room = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            current_room = 0
        if current_room > 0:
            continue

        metadata = metadata_rows.get(str(template_id)) or {}
        raw_affiliation = str(metadata.get("affiliation") or "").strip()
        segments = _affiliation_segments(raw_affiliation, metadata.get("hometown"))
        if not segments:
            continue
        location_hint = str(template.get("location_hint") or "").strip()
        require_area_match = bool(_metadata_area_groups(metadata)) and not location_hint
        room_tag_aliases = {
            _normalize_room_tag(value)
            for value in _lookup_affiliation_values(affiliation_room_tags, raw_affiliation)
            if str(value or "").strip()
        }
        room_title_aliases = [
            value
            for value in _lookup_affiliation_values(affiliation_room_titles, raw_affiliation)
            if str(value or "").strip()
        ]
        title_alias_norms = {_normalize_text(value) for value in room_title_aliases if value}

        best = None
        runner_up = -999
        for segment in segments:
            for segment_variant in _affiliation_segment_variants(segment, affiliation_aliases):
                segment_norm = _normalize_text(segment_variant)
                if not segment_norm:
                    continue
                for room in rooms_by_id.values():
                    title_norm = str(room.get("title_norm") or "")
                    if not title_norm:
                        continue
                    if not _affiliation_title_matches(segment_norm, room):
                        continue
                    if any(word in title_norm for word in _AFFILIATION_REJECT_TITLE_WORDS) and not any(
                        public_word in title_norm for public_word, _points in _AFFILIATION_PUBLIC_ROOM_WORDS
                    ):
                        continue
                    if require_area_match and not _metadata_matches_room(metadata, room):
                        continue
                    if location_hint and not _hint_matches_room(location_hint, room):
                        continue

                    score = 0
                    if title_norm == segment_norm:
                        score += 260
                    elif title_norm.startswith(f"{segment_norm},") or title_norm.startswith(f"{segment_norm} "):
                        score += 220
                    else:
                        score += 180

                    public_hit = False
                    for word, points in _AFFILIATION_PUBLIC_ROOM_WORDS:
                        if word in title_norm:
                            score += points
                            public_hit = True
                    if any(word in title_norm for word in _SHOP_BACKROOM_WORDS):
                        score -= 25
                    if any(title_norm.endswith(suffix) for suffix in _DIRECTIONAL_ROOM_SUFFIXES):
                        score -= 10
                    if len(segment_norm.split(" ")) == 1 and not public_hit:
                        continue
                    if _metadata_matches_room(metadata, room):
                        score += 20
                    if _hint_matches_room(location_hint, room):
                        score += 10

                    candidate = (score, int(room["room_id"]), title_norm)
                    if best is None or candidate[0] > best[0]:
                        if best is not None and best[2] != candidate[2]:
                            runner_up = max(runner_up, best[0])
                        best = candidate
                    elif best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, candidate[0])

        if title_alias_norms:
            for room in rooms_by_id.values():
                title_norm = str(room.get("title_norm") or "")
                if not title_norm:
                    continue
                if require_area_match and not _metadata_matches_room(metadata, room):
                    continue
                if location_hint and not _hint_matches_room(location_hint, room):
                    continue

                title_alias_hit = False
                for title_alias_norm in title_alias_norms:
                    if _affiliation_title_matches(title_alias_norm, room):
                        title_alias_hit = True
                        break
                if not title_alias_hit:
                    continue

                score = 255 + _room_public_bonus(title_norm)
                if _metadata_matches_room(metadata, room):
                    score += 20
                if _hint_matches_room(location_hint, room):
                    score += 10

                candidate = (score, int(room["room_id"]), title_norm)
                if best is None or candidate[0] > best[0]:
                    if best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, candidate[0])

        if room_tag_aliases:
            for room in rooms_by_id.values():
                title_norm = str(room.get("title_norm") or "")
                if not title_norm:
                    continue
                if require_area_match and not _metadata_matches_room(metadata, room):
                    continue
                if location_hint and not _hint_matches_room(location_hint, room):
                    continue

                tag_values = set(room.get("tag_values") or set())
                if not tag_values or not any(tag_value in tag_values for tag_value in room_tag_aliases):
                    continue

                title_alias_hit = False
                if title_alias_norms:
                    for title_alias_norm in title_alias_norms:
                        if _affiliation_title_matches(title_alias_norm, room):
                            title_alias_hit = True
                            break
                    if not title_alias_hit:
                        continue

                score = 260
                if title_alias_hit:
                    score += 35
                for word, points in _AFFILIATION_PUBLIC_ROOM_WORDS:
                    if word in title_norm:
                        score += points
                if any(word in title_norm for word in _SHOP_BACKROOM_WORDS):
                    score -= 25
                if any(title_norm.endswith(suffix) for suffix in _DIRECTIONAL_ROOM_SUFFIXES):
                    score -= 10
                if _metadata_matches_room(metadata, room):
                    score += 20
                if _hint_matches_room(location_hint, room):
                    score += 10

                candidate = (score, int(room["room_id"]), title_norm)
                if best is None or candidate[0] > best[0]:
                    if best is not None and best[2] != candidate[2]:
                        runner_up = max(runner_up, best[0])
                    best = candidate
                elif best is not None and best[2] != candidate[2]:
                    runner_up = max(runner_up, candidate[0])

        if best and runner_up <= best[0] - 2:
            resolved[str(template_id)] = int(best[1])

    log.info("npc_room_resolver: resolved %d NPC home rooms from affiliation institutions", len(resolved))
    return resolved
