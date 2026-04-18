"""
npc_manager.py
--------------
NPCManager — Spawns, tracks, and ticks all NPCs in the game world.

Load order at startup:
    1. Lua files  — scripts/npcs/**/*.lua  (authoritative for new NPCs)
    2. SQL table  — npcs registry + npc_state (room overrides, alive state)
    3. Hardcoded  — npc_data.NPC_TEMPLATES (legacy, backward-compat)
    Lua wins over hardcoded on template_id collision.

Per-tick responsibilities (every game tick = 0.1s):
    every  5s  — ambient emotes (can_emote)
    every  5s  — chat lines     (can_chat)
    every  1s  — patrol move check (can_wander, per-NPC move_interval gate)
    every  1s  — combat AI       (can_combat + in_combat)
    every 10s  — loot scan       (can_loot)
    every 10s  — bot AI step     (is_bot)
    every 60s  — guard shifts
    every 60s  — respawn check

Capabilities wired up in this file:
    [x] can_emote     — ambient emotes
    [x] can_chat      — random room speech
    [x] can_wander    — patrol movement with directional messages
    [x] can_combat    — attacks players/creatures, uses CombatEngine
    [x] can_loot      — collects silver from dead creatures in room
    [x] is_bot        — stub tick (flees when injured, returns to rest room)
    [ ] is_guild      — hooked, full implementation via quest engine
    [ ] is_quest      — hooked, full implementation via quest engine
    [ ] is_house      — stub
    [ ] is_invasion   — stub (invasion manager calls on_invasion hook)
"""

import random
import re
import time
import logging
import os
from typing import Dict, List, Optional

from server.core.entity.npc.npc import NPC
from server.core.entity.npc.npc_data import NPC_TEMPLATES
from server.core.entity.npc.npc_lua_loader import load_all_npc_luas
from server.core.scripting.loaders.npc_registry_loader import build_npc_registry_rows, sync_npc_registry
from server.core.scripting.loaders.npc_room_resolver import (
    _hint_matches_room,
    _load_room_index,
    resolve_npc_home_rooms,
    resolve_npc_home_rooms_from_affiliations,
    resolve_npc_home_rooms_from_location_hint_titles,
    resolve_npc_home_rooms_from_registry_affiliation_clusters,
    resolve_npc_home_rooms_from_registry_affiliation_segments,
    resolve_npc_home_rooms_from_registry_family_clusters,
    resolve_npc_home_rooms_from_role_tags,
    resolve_npc_home_rooms_from_template_prefixes,
    resolve_npc_home_rooms_from_template_title_overrides,
    resolve_npc_home_rooms_from_template_titles,
    resolve_npc_home_rooms_from_wiki_areas,
    resolve_npc_home_rooms_from_wiki_metadata,
)
from server.core.scripting.loaders.adventurers_guild_loader import load_adventurers_guild
from server.core.scripting.loaders.inns_loader import load_inns
from server.core.scripting.loaders.justice_loader import load_justice
from server.core.scripting.loaders.npc_service_roles_loader import load_npc_service_roles
from server.core.scripting.loaders.quest_npc_binding_loader import load_quest_npc_metadata
from server.core.scripting.loaders.travel_offices_loader import load_travel_offices
from server.core.protocol.colors import npc_emote, npc_speech, npc_name, colorize, TextPresets

log = logging.getLogger(__name__)

SHIFT_INTERVAL = 28800  # 8 hours in seconds

_GENERIC_SHOP_NAME_TOKENS = {
    "and", "armory", "bazaar", "bakeshop", "clothier", "company", "dry", "emporium",
    "exchange", "forging", "front", "furs", "general", "gems", "goods", "herbs",
    "jewelry", "locks", "magic", "market", "office", "other", "outfitters", "pawn",
    "pawnshop", "pelts", "sales", "shop", "stall", "store", "supply", "supplies",
    "tavern", "tinctures", "wares", "weaponry", "weavers", "women", "men",
}
_SHOPKEEPER_TEXT_TOKENS = {
    "armorer", "armourer", "baker", "bartender", "clerk", "dyer", "fletcher", "furrier",
    "gemcutter", "herbalist", "innkeeper", "jeweler", "jeweller", "locksmith",
    "merchant", "pawnbroker", "proprietor", "quartermaster", "seamstress", "shopkeeper",
    "smith", "tailor", "vendor", "weaponsmith",
}
_NON_SHOP_STAFF_TOKENS = {
    "browsing", "customer", "exploring", "guest", "patron", "shopper", "toddler", "tourist",
}
_NON_BANK_STAFF_TOKENS = {
    "audience", "bystander", "court", "guard", "guest", "noble", "sweeper", "visitor", "watch",
}
_SHOP_TYPE_HINTS = {
    "armor": ("armor", "armory", "armorer", "armourer", "fur", "furrier", "pelt", "smith"),
    "dye": ("dye", "dyer"),
    "food": ("baker", "bakeshop", "bartender", "cook", "food", "innkeeper", "tavern"),
    "gem": ("gem", "gemcutter", "jeweler", "jeweller"),
    "general": ("merchant", "shopkeeper", "storekeeper", "vendor"),
    "herb": ("apothecary", "herb", "herbalist", "tincture"),
    "magic": ("arcane", "magic", "mage", "sorcerer", "wizard"),
    "other": ("clerk", "merchant", "shopkeeper", "vendor"),
    "pawn": ("appraiser", "archivist", "pawnbroker", "proprietor"),
    "weapon": ("archery", "fletcher", "weapon", "weaponry", "weaponsmith"),
}

_DEPARTURE_BY_DIR = {
    "north": "heads north.", "south": "heads south.",
    "east":  "heads east.",  "west":  "heads west.",
    "up":    "heads upward.", "down": "heads downward.",
}
_ARRIVAL_BY_DIR = {
    "north": "arrives from the south.", "south": "arrives from the north.",
    "east":  "arrives from the west.",  "west":  "arrives from the east.",
    "up":    "arrives from below.",     "down":  "arrives from above.",
}

_SHIFT_DEPARTURE_LINES = {
    "amaranth": [
        "{name} hands over the post with a crisp salute.",
        "{name} gives a final scan of the road and steps aside.",
        "{name} murmurs a brief handoff report and departs.",
    ],
    "vermilion": [
        "{name} passes a quiet word to the incoming guard, then steps away.",
        "{name} gives a last look beyond the gate before departing.",
        "{name} straightens, salutes, and leaves the post.",
    ],
    "annatto": [
        "{name} lets out a long breath.  'Finally.'  The handoff is made.",
        "{name} brightens considerably at the sight of relief and hands over the post.",
        "{name} steps aside with visible relief.",
    ],
    "victory": [
        "{name} stands in place a moment after the relief arrives, then silently departs.",
        "{name} touches the gate wall once, then walks away.",
        "{name} passes the watch without ceremony.",
    ],
}

_SHIFT_ARRIVAL_LINES = {
    "amaranth": [
        "{name} takes the post with a nod.",
        "{name} arrives, shoulders straight, and assumes the watch.",
        "{name} settles into position at the Amaranth Gate.",
    ],
    "vermilion": [
        "{name} takes position at the Vermilion Gate without comment.",
        "{name} arrives and begins an immediate scan of the road beyond.",
        "{name} steps up and takes the watch.",
    ],
    "annatto": [
        "{name} arrives, surveys the empty road, and settles in.",
        "{name} takes up position with quiet efficiency.",
        "{name} assumes the post at the Annatto Gate.",
    ],
    "victory": [
        "{name} takes position at the Victory Gate.",
        "{name} arrives silently and assumes the watch.",
        "{name} settles into place at the Victory Gate.",
    ],
}


class NPCManager:
    """Manages all NPC instances in the game world."""

    def __init__(self, server):
        self.server = server
        self._npcs: Dict[int, NPC]            = {}   # npc_id  -> NPC
        self._room_npcs: Dict[int, List[int]] = {}   # room_id -> [npc_ids]
        self._template_to_id: Dict[str, int]  = {}   # template_id -> npc_id

        # Shift tracking
        self._shift_phase:  Dict[str, int]          = {}
        self._shift_guards: Dict[str, Dict[int, int]] = {}
        self._last_shift_time = time.time()

        # Stats for logging
        self._lua_count    = 0
        self._sql_count    = 0
        self._legacy_count = 0
        self._skipped_invalid_room = 0
        self._authoritative_home_rooms: Dict[str, int] = {}
        self._authoritative_room_sources: Dict[str, str] = {}

    # ── Initialisation ────────────────────────────────────────────────────────

    async def initialize(self):
        """Load all NPC templates, restore SQL state, spawn into world."""
        scripts_path = self.server.config.get("paths.scripts", "./scripts")

        # ── Phase 1: Lua NPC files (authoritative) ────────────────────────────
        lua_templates = load_all_npc_luas(scripts_path)
        justice_mgr = getattr(self.server, "justice", None)
        if justice_mgr:
            try:
                for tid, template in (justice_mgr.get_npc_templates() or {}).items():
                    if tid:
                        lua_templates[str(tid)] = dict(template)
            except Exception:
                log.exception("NPCManager: failed loading justice NPC templates")
        self._lua_count = len(lua_templates)

        # ── Phase 3: Legacy hardcoded templates (NPC_TEMPLATES in npc_data.py) ─
        all_templates: Dict[str, dict] = {}
        for t in NPC_TEMPLATES:
            tid = t.get("template_id", "")
            if tid and tid not in lua_templates:
                all_templates[tid] = t
                self._legacy_count += 1

        # Lua wins on collision
        all_templates.update(lua_templates)

        registry_snapshot = self._load_sql_registry()
        self._load_authoritative_room_index(scripts_path, all_templates, registry_snapshot)
        room_index = _load_room_index(scripts_path)
        rooms_by_id = dict((room_index or {}).get("rooms_by_id") or {})
        self._apply_authoritative_room_overrides(all_templates, rooms_by_id)

        registry_templates = {tid: dict(template) for tid, template in lua_templates.items()}
        self._apply_authoritative_room_overrides(registry_templates, rooms_by_id)
        self._enrich_templates_from_authoritative_sources(registry_templates, scripts_path)

        try:
            synced = sync_npc_registry(
                getattr(self.server, "db", None),
                build_npc_registry_rows(registry_templates, scripts_path, world=getattr(self.server, "world", None)),
                scripts_path=scripts_path,
            )
            log.info("NPC registry synced from Lua (%d templates)", synced)
        except Exception:
            log.exception("NPCManager: failed syncing npc registry from Lua")

        # ── Phase 2: SQL registry/state (room overrides + enable flags + alive state) ──
        sql_registry = self._load_sql_registry()
        sql_state = self._load_sql_state()
        self._sql_count = len(sql_state)

        disabled_templates = set()
        for tid, row in sql_registry.items():
            if not bool(row.get("enabled", True)):
                disabled_templates.add(tid)
            if tid in all_templates and row.get("home_room_id"):
                all_templates[tid]["room_id"] = int(row["home_room_id"])
                all_templates[tid]["home_room_id"] = int(row["home_room_id"])
                if row.get("location_hint") and not all_templates[tid].get("location_hint"):
                    all_templates[tid]["location_hint"] = str(row["location_hint"]).strip()

        # Apply SQL room overrides to templates
        for tid, state in sql_state.items():
            if tid in all_templates and state.get("current_room_id"):
                all_templates[tid]["room_id"]      = state["current_room_id"]
                all_templates[tid]["home_room_id"]  = state["current_room_id"]

        self._enrich_templates_from_authoritative_sources(all_templates, scripts_path)

        # ── Phase 4: Spawn ────────────────────────────────────────────────────
        spawned = skipped_relief = skipped_rare = skipped_dead = 0

        for tid, template in all_templates.items():
            if tid in disabled_templates:
                continue

            # Skip if SQL says dead and not yet respawned
            state = sql_state.get(tid, {})
            if state and not state.get("is_alive", True):
                respawn_at = state.get("respawn_at", 0)
                if respawn_at > time.time():
                    skipped_dead += 1
                    continue

            # Relief guards don't spawn at startup — registered for shift system
            if not template.get("spawn_at_start", True):
                self._register_shift_guard(template, npc_instance=None)
                skipped_relief += 1
                continue

            # Rare spawn roll
            if template.get("rare_spawn", False):
                if random.random() > template.get("spawn_chance", 1.0):
                    skipped_rare += 1
                    continue

            template = self._normalize_template(template)
            if template is None:
                self._skipped_invalid_room += 1
                continue

            npc = NPC(template)
            self._attach_lua_runtime(npc, template)
            self._place_npc(npc)

            if npc.shift_id:
                self._register_shift_guard(template, npc_instance=npc)

            spawned += 1

        log.info(
            "NPCManager initialized: %d spawned (%d Lua, %d SQL overrides, %d legacy) "
            "%d relief pending, %d rare skipped, %d dead/respawning, %d invalid-room skipped",
            spawned, self._lua_count, self._sql_count, self._legacy_count,
            skipped_relief, skipped_rare, skipped_dead, self._skipped_invalid_room,
        )

    # ── SQL state ─────────────────────────────────────────────────────────────

    def _load_sql_state(self) -> dict:
        """Load npc_state table. Returns {template_id: state_dict}."""
        db = getattr(self.server, "db", None)
        if not db:
            return {}
        try:
            conn = db._get_conn()
            cur  = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT template_id, is_alive, current_room_id, respawn_at "
                "FROM npc_state"
            )
            rows = cur.fetchall()
            conn.close()
            return {r["template_id"]: r for r in rows}
        except Exception as e:
            log.warning("NPCManager: could not load npc_state: %s", e)
            return {}

    def _load_sql_registry(self) -> dict:
        """Load npcs table. Returns {template_id: registry_row}."""
        db = getattr(self.server, "db", None)
        if not db:
            return {}
        try:
            conn = db._get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SHOW COLUMNS FROM npcs")
            columns = {str(row.get('Field') or '').strip().lower() for row in (cur.fetchall() or [])}
            has_display_name = "display_name" in columns
            has_location_hint = "location_hint" in columns
            select_cols = ["template_id", "home_room_id", "enabled"]
            if has_display_name:
                select_cols.append("display_name")
            if has_location_hint:
                select_cols.append("location_hint")
            cur.execute(f"SELECT {', '.join(select_cols)} FROM npcs")
            rows = cur.fetchall()
            conn.close()
            return {str(r["template_id"]).strip(): r for r in rows if str(r.get("template_id") or "").strip()}
        except Exception as e:
            log.warning("NPCManager: could not load npc registry: %s", e)
            return {}

    def _save_npc_state(self, npc: NPC):
        """Upsert one row in npc_state."""
        db = getattr(self.server, "db", None)
        if not db:
            return
        try:
            db.execute_update(
                """INSERT INTO npc_state (template_id, is_alive, current_room_id, respawn_at)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                       is_alive=VALUES(is_alive),
                       current_room_id=VALUES(current_room_id),
                       respawn_at=VALUES(respawn_at)""",
                (
                    npc.template_id,
                    1 if npc.alive else 0,
                    npc.room_id,
                    int(npc.death_time + npc.respawn_seconds) if not npc.alive else 0,
                )
            )
        except Exception as e:
            log.warning("NPCManager: npc_state save failed for %s: %s", npc.template_id, e)

    def _room_exists(self, room_id: int) -> bool:
        try:
            return bool(room_id) and self.server.world.get_room(int(room_id)) is not None
        except Exception:
            return False

    def _merge_authoritative_room_map(self, room_map: dict[str, int], source_name: str):
        added = conflicts = 0
        for template_id, room_id in sorted((room_map or {}).items()):
            template_id = str(template_id or "").strip()
            try:
                room_id = int(room_id or 0)
            except (TypeError, ValueError):
                continue
            if not template_id or room_id <= 0:
                continue
            existing = self._authoritative_home_rooms.get(template_id)
            if existing and existing != room_id:
                conflicts += 1
                log.debug(
                    "NPCManager: keeping authoritative room %s=%s (%s) over %s (%s)",
                    template_id,
                    existing,
                    self._authoritative_room_sources.get(template_id, "unknown"),
                    room_id,
                    source_name,
                )
                continue
            if existing:
                continue
            self._authoritative_home_rooms[template_id] = room_id
            self._authoritative_room_sources[template_id] = source_name
            added += 1
        return added, conflicts

    def _load_shop_room_index(self, templates: Dict[str, dict]) -> dict[str, int]:
        db = getattr(self.server, "db", None)
        if not db or not templates:
            return {}
        try:
            conn = db._get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, room_id FROM shops WHERE is_active = 1 AND room_id > 0")
            shop_rows = cur.fetchall()
            conn.close()
        except Exception as e:
            log.warning("NPCManager: could not load shop room index: %s", e)
            return {}

        by_shop_id = {}
        for row in shop_rows:
            try:
                shop_id = int(row.get("id") or 0)
                room_id = int(row.get("room_id") or 0)
            except (TypeError, ValueError):
                continue
            if shop_id > 0 and room_id > 0:
                by_shop_id[shop_id] = room_id

        out: dict[str, int] = {}
        for template_id, template in templates.items():
            try:
                shop_id = int(template.get("shop_id") or 0)
            except (TypeError, ValueError):
                continue
            room_id = by_shop_id.get(shop_id)
            if room_id and self._room_exists(room_id):
                out[str(template_id)] = room_id
        return out

    def _load_guild_room_index(self) -> dict[str, int]:
        db = getattr(self.server, "db", None)
        if not db:
            return {}
        try:
            conn = db._get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT npc_template_id, room_id "
                "FROM guild_master_registry "
                "WHERE is_active = 1 AND room_id > 0"
            )
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            log.warning("NPCManager: could not load guild room index: %s", e)
            return {}

        out: dict[str, int] = {}
        for row in rows:
            template_id = str(row.get("npc_template_id") or "").strip()
            try:
                room_id = int(row.get("room_id") or 0)
            except (TypeError, ValueError):
                continue
            if template_id and room_id > 0 and self._room_exists(room_id):
                out[template_id] = room_id
        return out

    def _load_travel_office_room_index(self) -> dict[str, int]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        data = load_travel_offices(engine)
        out: dict[str, int] = {}
        for office in (data.get("offices") or {}).values():
            template_id = str(office.get("clerk_template_id") or "").strip()
            try:
                room_id = int(office.get("room_id") or 0)
            except (TypeError, ValueError):
                continue
            if template_id and room_id > 0 and self._room_exists(room_id):
                out[template_id] = room_id
        return out

    def _load_inn_room_index(self) -> dict[str, int]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        data = load_inns(engine)
        out: dict[str, int] = {}
        for inn in (data.get("inns") or {}).values():
            try:
                room_id = int(inn.get("front_desk_room_id") or 0)
            except (TypeError, ValueError):
                continue
            if room_id <= 0 or not self._room_exists(room_id):
                continue
            for template_id in inn.get("innkeeper_template_ids") or []:
                template_id = str(template_id or "").strip()
                if template_id:
                    out[template_id] = room_id
        return out

    def _load_adventurers_guild_room_index(self) -> dict[str, int]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        try:
            data = load_adventurers_guild(engine)
        except Exception as e:
            log.warning("NPCManager: could not load Adventurer's Guild room index: %s", e)
            return {}
        out: dict[str, int] = {}
        for authority in (data or {}).get("authorities", {}).values():
            template_id = str(authority.get("template_id") or "").strip()
            try:
                room_id = int(authority.get("room_id") or 0)
            except (TypeError, ValueError):
                continue
            if template_id and room_id > 0 and self._room_exists(room_id):
                out[template_id] = room_id
        return out

    def _load_quest_room_index(self, scripts_path: str) -> dict[str, int]:
        room_map, _template_ids = self._load_quest_npc_metadata(scripts_path)
        return room_map

    def _load_quest_npc_metadata(self, scripts_path: str) -> tuple[dict[str, int], set[str]]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        metadata = load_quest_npc_metadata(engine, scripts_path)
        room_map = dict(metadata.get("bindings") or {})
        valid_room_map = {
            template_id: room_id
            for template_id, room_id in room_map.items()
            if self._room_exists(room_id)
        }
        template_ids = {
            str(template_id or "").strip()
            for template_id in (metadata.get("template_ids") or set())
            if str(template_id or "").strip()
        }
        return valid_room_map, template_ids

    def _apply_authoritative_room_overrides(self, templates: Dict[str, dict], rooms_by_id: dict[int, dict]):
        for tid, template in (templates or {}).items():
            try:
                home_room_id = int(template.get("home_room_id") or template.get("room_id") or 0)
            except (TypeError, ValueError):
                home_room_id = 0
            resolved_room = int(self._authoritative_home_rooms.get(tid) or 0)
            location_hint = str(template.get("location_hint") or "").strip()
            current_room = rooms_by_id.get(home_room_id) if home_room_id > 0 else None
            authoritative_room = rooms_by_id.get(resolved_room) if resolved_room > 0 else None
            current_hint_mismatch = bool(
                location_hint and current_room and not _hint_matches_room(location_hint, current_room)
            )
            authoritative_hint_match = bool(
                location_hint and authoritative_room and _hint_matches_room(location_hint, authoritative_room)
            )
            if resolved_room > 0 and (
                home_room_id <= 0
                or (current_hint_mismatch and authoritative_hint_match)
            ):
                template["home_room_id"] = resolved_room
                template["room_id"] = resolved_room

    def _load_active_shop_index(self) -> dict[int, dict]:
        db = getattr(self.server, "db", None)
        if not db:
            return {}
        try:
            conn = db._get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, name, room_id, shop_type "
                "FROM shops "
                "WHERE is_active = 1 AND room_id > 0"
            )
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            log.warning("NPCManager: could not load active shop metadata: %s", e)
            return {}

        by_room: dict[int, dict] = {}
        ambiguous_rooms: set[int] = set()
        for row in rows or []:
            try:
                room_id = int(row.get("room_id") or 0)
                shop_id = int(row.get("id") or 0)
            except (TypeError, ValueError):
                continue
            if room_id <= 0 or shop_id <= 0:
                continue
            if room_id in ambiguous_rooms:
                continue
            if room_id in by_room:
                by_room.pop(room_id, None)
                ambiguous_rooms.add(room_id)
                continue
            by_room[room_id] = {
                "shop_id": shop_id,
                "room_id": room_id,
                "name": str(row.get("name") or "").strip(),
                "shop_type": str(row.get("shop_type") or "").strip().lower(),
            }
        return by_room

    def _template_shop_affinity(self, template: dict, shop_row: dict) -> int:
        try:
            current_shop_id = int(template.get("shop_id") or 0)
        except (TypeError, ValueError):
            current_shop_id = 0
        if current_shop_id > 0:
            return 100 if current_shop_id == int(shop_row.get("shop_id") or 0) else -100

        text = " ".join(
            str(template.get(field) or "").strip().lower()
            for field in ("template_id", "name", "title", "description", "role", "location_hint")
        )
        score = 0

        if bool(template.get("can_shop")):
            score += 20

        service_tags = {
            str(tag or "").strip().lower()
            for tag in (template.get("service_tags") or [])
            if str(tag or "").strip()
        }
        if "shop" in service_tags or "pawnbroker" in service_tags:
            score += 15

        for token in _SHOPKEEPER_TEXT_TOKENS:
            if token in text:
                score += 4

        shop_type = str(shop_row.get("shop_type") or "").strip().lower()
        for token in _SHOP_TYPE_HINTS.get(shop_type, ()):
            if token and token in text:
                score += 3

        shop_name = str(shop_row.get("name") or "").lower()
        for token in re.split(r"[^a-z0-9]+", shop_name):
            token = token.strip()
            if len(token) < 3 or token in _GENERIC_SHOP_NAME_TOKENS:
                continue
            if token in text:
                score += 5

        return score

    def _is_counter_service_npc(self, template: dict, shop_row: dict, score: int) -> bool:
        try:
            current_shop_id = int(template.get("shop_id") or 0)
        except (TypeError, ValueError):
            current_shop_id = 0
        if current_shop_id > 0:
            return True
        if bool(template.get("can_shop")):
            return True

        text = " ".join(
            str(template.get(field) or "").strip().lower()
            for field in ("template_id", "name", "title", "description")
        )
        if any(token in text for token in _NON_SHOP_STAFF_TOKENS):
            return False

        explicit_staff_markers = (
            "proprietor", "shop", "shopkeeper", "merchant", "vendor", "clerk", "furrier", "inventory",
            "wares", "supply", "supply shop", "goods", "pawnbroker",
        )
        if any(marker in text for marker in explicit_staff_markers):
            return score >= 6

        shop_type = str(shop_row.get("shop_type") or "").strip().lower()
        if shop_type in {"herb", "armor", "weapon", "pawn", "food", "gem"}:
            if score >= 8 and any(token in text for token in _SHOP_TYPE_HINTS.get(shop_type, ())):
                return True

        return False

    def _load_shop_capability_index(self, templates: Dict[str, dict]) -> dict[str, dict]:
        shop_rows_by_room = self._load_active_shop_index()
        if not shop_rows_by_room or not templates:
            return {}

        room_templates: dict[int, list[tuple[str, dict]]] = {}
        for template_id, template in templates.items():
            try:
                room_id = int(template.get("home_room_id") or template.get("room_id") or 0)
            except (TypeError, ValueError):
                continue
            if room_id > 0:
                room_templates.setdefault(room_id, []).append((str(template_id), template))

        overrides: dict[str, dict] = {}
        for room_id, shop_row in shop_rows_by_room.items():
            occupants = room_templates.get(room_id) or []
            if not occupants:
                continue

            chosen: list[tuple[str, dict]] = []
            for template_id, template in occupants:
                score = self._template_shop_affinity(template, shop_row)
                if len(occupants) == 1:
                    if score >= 0:
                        chosen.append((template_id, template))
                    continue
                if self._is_counter_service_npc(template, shop_row, score):
                    chosen.append((template_id, template))

            if not chosen:
                continue

            shop_id = int(shop_row.get("shop_id") or 0)
            for template_id, template in chosen:
                try:
                    current_shop_id = int(template.get("shop_id") or 0)
                except (TypeError, ValueError):
                    current_shop_id = 0
                if current_shop_id > 0 and current_shop_id != shop_id:
                    continue

                service_tags = {
                    str(tag or "").strip().lower()
                    for tag in (template.get("service_tags") or [])
                    if str(tag or "").strip()
                }
                service_tags.add("shop")
                if str(shop_row.get("shop_type") or "").strip().lower() == "pawn":
                    service_tags.add("pawnbroker")
                lua_context = dict(template.get("lua_context") or {})
                lua_context["shop_binding_source"] = "shops_room_id"
                overrides[template_id] = {
                    "can_shop": True,
                    "shop_id": shop_id,
                    "role": "shopkeeper",
                    "service_tags": sorted(service_tags),
                    "lua_context": lua_context,
                }
        return overrides

    @staticmethod
    def _merge_service_tags(*groups) -> list[str]:
        merged = {
            str(tag or "").strip().lower()
            for group in groups
            for tag in (group or [])
            if str(tag or "").strip()
        }
        return sorted(merged)

    @staticmethod
    def _merge_lua_context(*groups) -> dict:
        merged: dict = {}
        for group in groups:
            if isinstance(group, dict):
                merged.update(group)
        return merged

    @staticmethod
    def _should_override_role(current_role: str, replacement_role: str) -> bool:
        current = str(current_role or "").strip().lower()
        replacement = str(replacement_role or "").strip().lower()
        if not replacement:
            return False
        if not current:
            return True
        return current in {"commoner", "citizen", "npc", "townsfolk"}

    def _apply_capability_patch(self, template: dict, patch: dict):
        if not template or not patch:
            return

        if "service_tags" in patch:
            template["service_tags"] = self._merge_service_tags(
                template.get("service_tags") or [],
                patch.get("service_tags") or [],
            )

        if "lua_context" in patch:
            template["lua_context"] = self._merge_lua_context(
                template.get("lua_context") or {},
                patch.get("lua_context") or {},
            )

        for flag in ("can_shop", "is_guild", "is_quest"):
            if flag in patch:
                template[flag] = bool(template.get(flag) or patch.get(flag))

        for field in ("shop_id", "guild_id", "justice_role", "justice_jurisdiction"):
            value = patch.get(field)
            if value in (None, "", 0):
                continue
            current = template.get(field)
            if current in (None, "", 0, False) or current == value:
                template[field] = value

        replacement_role = str(patch.get("role") or "").strip()
        if replacement_role and self._should_override_role(template.get("role"), replacement_role):
            template["role"] = replacement_role

    def _load_inn_capability_index(self) -> dict[str, dict]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        data = load_inns(engine)
        overrides: dict[str, dict] = {}
        for inn in (data.get("inns") or {}).values():
            inn_id = str(inn.get("id") or "").strip().lower()
            room_id = int(inn.get("front_desk_room_id") or 0)
            if not inn_id or room_id <= 0 or not self._room_exists(room_id):
                continue
            for template_id in inn.get("innkeeper_template_ids") or []:
                template_id = str(template_id or "").strip()
                if not template_id:
                    continue
                overrides[template_id] = {
                    "service_tags": ["inn"],
                    "role": "innkeeper",
                    "lua_context": {
                        "inn_binding_source": "inns_lua",
                        "inn_id": inn_id,
                    },
                }
        return overrides

    def _load_travel_capability_index(self) -> dict[str, dict]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        data = load_travel_offices(engine)
        overrides: dict[str, dict] = {}
        for office in (data.get("offices") or {}).values():
            template_id = str(office.get("clerk_template_id") or "").strip()
            office_id = str(office.get("id") or "").strip().lower()
            network = str(office.get("network") or "").strip().lower()
            room_id = int(office.get("room_id") or 0)
            if not template_id or not office_id or room_id <= 0 or not self._room_exists(room_id):
                continue
            overrides[template_id] = {
                "service_tags": ["travel"],
                "role": "travel_clerk",
                "lua_context": {
                    "travel_binding_source": "travel_offices_lua",
                    "travel_office_id": office_id,
                    "travel_network": network,
                },
            }
        return overrides

    def _load_adventurers_guild_capability_index(self) -> dict[str, dict]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        try:
            data = load_adventurers_guild(engine)
        except Exception as e:
            log.warning("NPCManager: could not load Adventurer's Guild capability index: %s", e)
            return {}

        overrides: dict[str, dict] = {}
        for authority in (data or {}).get("authorities", {}).values():
            template_id = str(authority.get("template_id") or "").strip()
            room_id = int(authority.get("room_id") or 0)
            role = str(authority.get("role") or "taskmaster").strip().lower()
            town_name = str(authority.get("town_name") or "").strip()
            if not template_id or room_id <= 0 or not self._room_exists(room_id):
                continue
            service_tags = ["guild", "adventurers_guild"]
            if role:
                service_tags.append(role)
            overrides[template_id] = {
                "is_guild": True,
                "guild_id": "adventurers",
                "role": role or "taskmaster",
                "service_tags": service_tags,
                "lua_context": {
                    "guild_binding_source": "adventurers_guild_lua",
                    "guild_role_type": role,
                    "guild_town_name": town_name,
                },
            }
        return overrides

    def _load_guild_registry_capability_index(self) -> dict[str, dict]:
        db = getattr(self.server, "db", None)
        if not db:
            return {}
        try:
            conn = db._get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT guild_id, role_type, npc_template_id, room_id "
                "FROM guild_master_registry "
                "WHERE is_active = 1 AND room_id > 0"
            )
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            log.warning("NPCManager: could not load guild capability index: %s", e)
            return {}

        overrides: dict[str, dict] = {}
        for row in rows or []:
            template_id = str(row.get("npc_template_id") or "").strip()
            guild_id = str(row.get("guild_id") or "").strip().lower()
            role_type = str(row.get("role_type") or "").strip().lower()
            try:
                room_id = int(row.get("room_id") or 0)
            except (TypeError, ValueError):
                room_id = 0
            if not template_id or not guild_id or room_id <= 0 or not self._room_exists(room_id):
                continue
            service_tags = ["guild", guild_id]
            if role_type:
                service_tags.append(role_type)
            overrides[template_id] = {
                "is_guild": True,
                "guild_id": guild_id,
                "role": role_type or "guild_authority",
                "service_tags": service_tags,
                "lua_context": {
                    "guild_binding_source": "guild_master_registry",
                    "guild_role_type": role_type,
                },
            }
        return overrides

    def _load_justice_capability_index(self) -> dict[str, dict]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        data = load_justice(engine)
        overrides: dict[str, dict] = {}
        for template_id, npc_row in (data.get("npcs") or {}).items():
            template_id = str(template_id or "").strip()
            room_id = int(npc_row.get("room_id") or 0)
            if not template_id or room_id <= 0 or not self._room_exists(room_id):
                continue
            justice_role = str(npc_row.get("justice_role") or "").strip().lower()
            justice_jurisdiction = str(npc_row.get("justice_jurisdiction") or "").strip().lower()
            service_tags = list(npc_row.get("service_tags") or [])
            service_tags.append("justice")
            if justice_role:
                service_tags.append(justice_role)
            overrides[template_id] = {
                "role": justice_role or "justice",
                "service_tags": service_tags,
                "justice_role": justice_role,
                "justice_jurisdiction": justice_jurisdiction,
                "lua_context": self._merge_lua_context(
                    npc_row.get("lua_context") or {},
                    {"justice_binding_source": "justice_lua"},
                ),
            }
        return overrides

    def _load_npc_service_capability_index(self) -> dict[str, dict]:
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        data = load_npc_service_roles(engine)
        overrides: dict[str, dict] = {}
        for template_id, row in (data.get("templates") or {}).items():
            template_id = str(template_id or "").strip()
            if not template_id:
                continue
            overrides[template_id] = {
                "role": str(row.get("role") or "").strip(),
                "service_tags": list(row.get("service_tags") or []),
                "lua_context": self._merge_lua_context(
                    row.get("lua_context") or {},
                    {"service_binding_source": "npc_services_lua"},
                ),
            }
        return overrides

    def _load_bank_room_ids(self) -> set[int]:
        db = getattr(self.server, "db", None)
        if not db:
            return set()
        try:
            conn = db._get_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT room_id "
                "FROM public_locker_rooms "
                "WHERE room_role = 'bank' AND room_id > 0"
            )
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            log.warning("NPCManager: could not load bank room index: %s", e)
            return set()
        out: set[int] = set()
        for row in rows or []:
            try:
                room_id = int((row[0] if isinstance(row, (list, tuple)) else row.get("room_id")) or 0)
            except Exception:
                room_id = 0
            if room_id > 0 and self._room_exists(room_id):
                out.add(room_id)
        return out

    def _template_bank_affinity(self, template: dict) -> int:
        text = " ".join(
            str(template.get(field) or "").strip().lower()
            for field in ("template_id", "name", "title", "description", "role", "location_hint")
        )
        if any(token in text for token in _NON_BANK_STAFF_TOKENS):
            return -100

        score = 0
        service_tags = {
            str(tag or "").strip().lower()
            for tag in (template.get("service_tags") or [])
            if str(tag or "").strip()
        }
        if "bank" in service_tags:
            score += 50
        if any(marker in text for marker in ("bank clerk", "bank teller", "united bank", "teller", "ledger")):
            score += 20
        if "bank" in text:
            score += 12
        if "clerk" in text:
            score += 8
        return score

    def _load_bank_capability_index(self, templates: Dict[str, dict]) -> dict[str, dict]:
        bank_room_ids = self._load_bank_room_ids()
        if not bank_room_ids or not templates:
            return {}

        room_templates: dict[int, list[tuple[str, dict]]] = {}
        for template_id, template in templates.items():
            try:
                room_id = int(template.get("home_room_id") or template.get("room_id") or 0)
            except (TypeError, ValueError):
                continue
            if room_id in bank_room_ids:
                room_templates.setdefault(room_id, []).append((str(template_id), template))

        overrides: dict[str, dict] = {}
        for room_id, occupants in room_templates.items():
            chosen: list[str] = []
            for template_id, template in occupants:
                score = self._template_bank_affinity(template)
                if len(occupants) == 1:
                    if score >= 0:
                        chosen.append(template_id)
                    continue
                if score >= 18:
                    chosen.append(template_id)
            for template_id in chosen:
                overrides[template_id] = {
                    "service_tags": ["bank"],
                    "role": "bank_clerk",
                    "lua_context": {
                        "bank_binding_source": "public_locker_rooms",
                        "bank_room_id": room_id,
                    },
                }
        return overrides

    def _enrich_templates_from_authoritative_sources(self, templates: Dict[str, dict], scripts_path: str):
        if not templates:
            return

        _quest_room_map, quest_template_ids = self._load_quest_npc_metadata(scripts_path)
        quest_updates = 0
        for template_id in quest_template_ids:
            template = templates.get(template_id)
            if not template:
                continue
            if not bool(template.get("is_quest")):
                quest_updates += 1
            template["is_quest"] = True
            lua_context = dict(template.get("lua_context") or {})
            lua_context["quest_binding_source"] = "quest_lua"
            template["lua_context"] = lua_context

        capability_sources = {
            "npc_services": self._load_npc_service_capability_index(),
            "shop": self._load_shop_capability_index(templates),
            "inn": self._load_inn_capability_index(),
            "travel": self._load_travel_capability_index(),
            "adventurers_guild": self._load_adventurers_guild_capability_index(),
            "guild_registry": self._load_guild_registry_capability_index(),
            "justice": self._load_justice_capability_index(),
            "bank": self._load_bank_capability_index(templates),
        }
        counts: dict[str, int] = {}
        for source_name, overrides in capability_sources.items():
            applied = 0
            for template_id, patch in overrides.items():
                template = templates.get(template_id)
                if not template:
                    continue
                self._apply_capability_patch(template, patch)
                applied += 1
            counts[source_name] = applied

        log.info(
            "NPCManager: enriched %d templates from quest Lua, npc_services=%d, shop=%d, inn=%d, travel=%d, adventurers_guild=%d, guild_registry=%d, justice=%d, bank=%d",
            quest_updates,
            counts.get("npc_services", 0),
            counts.get("shop", 0),
            counts.get("inn", 0),
            counts.get("travel", 0),
            counts.get("adventurers_guild", 0),
            counts.get("guild_registry", 0),
            counts.get("justice", 0),
            counts.get("bank", 0),
        )

    def _load_authoritative_room_index(
        self,
        scripts_path: str,
        templates: Dict[str, dict],
        registry_rows: Dict[str, dict] | None = None,
    ):
        self._authoritative_home_rooms = {}
        self._authoritative_room_sources = {}

        counts = []
        for source_name, room_map in (
            ("guild_master_registry", self._load_guild_room_index()),
            ("shops", self._load_shop_room_index(templates)),
            ("travel_offices", self._load_travel_office_room_index()),
            ("inns", self._load_inn_room_index()),
            ("adventurers_guild", self._load_adventurers_guild_room_index()),
            ("quest_bindings", self._load_quest_room_index(scripts_path)),
            ("location_hint_hubs", resolve_npc_home_rooms_from_location_hint_titles(templates, scripts_path)),
            ("template_room_title_overrides", resolve_npc_home_rooms_from_template_title_overrides(templates, scripts_path)),
            ("template_room_prefixes", resolve_npc_home_rooms_from_template_prefixes(templates, scripts_path)),
            ("template_room_titles", resolve_npc_home_rooms_from_template_titles(templates, scripts_path)),
            ("wiki_shop_titles", resolve_npc_home_rooms_from_wiki_metadata(templates, scripts_path)),
            ("wiki_affiliations", resolve_npc_home_rooms_from_affiliations(templates, scripts_path)),
            ("registry_affiliation_clusters", resolve_npc_home_rooms_from_registry_affiliation_clusters(templates, registry_rows or {}, scripts_path)),
            ("registry_affiliation_segments", resolve_npc_home_rooms_from_registry_affiliation_segments(templates, registry_rows or {}, scripts_path)),
            ("registry_family_clusters", resolve_npc_home_rooms_from_registry_family_clusters(templates, registry_rows or {}, scripts_path)),
            ("role_tag_shops", resolve_npc_home_rooms_from_role_tags(templates, scripts_path)),
            ("wiki_area_hubs", resolve_npc_home_rooms_from_wiki_areas(templates, scripts_path)),
            ("room_graph_titles", resolve_npc_home_rooms(templates, scripts_path)),
        ):
            added, conflicts = self._merge_authoritative_room_map(room_map, source_name)
            counts.append((source_name, added, conflicts))

        summary = ", ".join(
            f"{source}={added}" + (f"/{conflicts} conflicts" if conflicts else "")
            for source, added, conflicts in counts
        )
        log.info(
            "NPCManager: authoritative room index ready for %d templates (%s)",
            len(self._authoritative_home_rooms),
            summary,
        )

    def _normalize_template(self, template: dict) -> Optional[dict]:
        normalized = dict(template)

        template_id = str(normalized.get("template_id") or "").strip()
        home_room = int(normalized.get("home_room_id") or normalized.get("room_id") or 0)
        patrol_rooms = []
        for room_id in normalized.get("patrol_rooms", []) or []:
            try:
                room_id = int(room_id)
            except (TypeError, ValueError):
                continue
            if self._room_exists(room_id) and room_id not in patrol_rooms:
                patrol_rooms.append(room_id)

        if not self._room_exists(home_room) and template_id:
            resolved_room = int(self._authoritative_home_rooms.get(template_id) or 0)
            if self._room_exists(resolved_room):
                home_room = resolved_room
                lua_context = dict(normalized.get("lua_context") or {})
                lua_context["placement_source"] = self._authoritative_room_sources.get(template_id, "authoritative_index")
                normalized["lua_context"] = lua_context

        if not self._room_exists(home_room):
            if patrol_rooms:
                home_room = patrol_rooms[0]
            else:
                label = normalized.get("lua_file") or normalized.get("template_id", "unknown_npc")
                log.debug("Skipping NPC %s due to invalid home room id %s", label, normalized.get("home_room_id"))
                return None

        normalized["home_room_id"] = home_room
        normalized["room_id"] = home_room
        normalized["patrol_rooms"] = patrol_rooms

        if normalized.get("can_wander") and len(patrol_rooms) < 2:
            normalized["can_wander"] = False

        return normalized

    def _attach_lua_runtime(self, npc: NPC, template: dict):
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        if not engine or not engine.available:
            return

        lua_module = template.get("lua_module")
        lua_file = template.get("lua_file")
        lua_context = dict(template.get("lua_context") or {})
        try:
            if lua_file and os.path.exists(lua_file):
                npc._lua_table = engine.load_file(lua_file)
            elif lua_module:
                if lua_context:
                    scripts_path = os.path.abspath(self.server.config.get("paths.scripts", "./scripts"))
                    module_rel = str(lua_module).replace(".", os.sep) + ".lua"
                    module_file = os.path.join(scripts_path, module_rel)
                    if os.path.exists(module_file):
                        npc._lua_table = engine.load_file(module_file)
                    else:
                        npc._lua_table = engine.require(lua_module)
                else:
                    npc._lua_table = engine.require(lua_module)
        except Exception as e:
            log.error("NPC Lua load failed (%s): %s", npc.template_id, e)
            npc._lua_table = None
            return

        if npc._lua_table and lua_context:
            try:
                ctx = engine.python_to_lua(lua_context)
                attached = engine.call_npc_hook(npc._lua_table, "attach", ctx)
                if attached is not None:
                    npc._lua_table = attached
                else:
                    engine.call_npc_hook(npc._lua_table, "configure", ctx)
            except Exception as e:
                log.error("NPC attach/configure hook error (%s): %s", npc.template_id, e)

        if npc._lua_table and npc.has_hook("on_load"):
            try:
                engine.call_npc_hook(npc._lua_table, "on_load")
            except Exception as e:
                log.error("NPC on_load hook error (%s): %s", npc.template_id, e)

    # ── World index helpers ────────────────────────────────────────────────────

    def _place_npc(self, npc: NPC):
        self._npcs[npc.id] = npc
        self._template_to_id[npc.template_id] = npc.id
        self._room_npcs.setdefault(npc.room_id, []).append(npc.id)

    def _remove_npc(self, npc: NPC):
        self._npcs.pop(npc.id, None)
        self._template_to_id.pop(npc.template_id, None)
        room_list = self._room_npcs.get(npc.room_id, [])
        if npc.id in room_list:
            room_list.remove(npc.id)

    def _move_npc_index(self, npc: NPC, new_room_id: int):
        """Update the room index only — does not broadcast."""
        old_room = npc.room_id
        room_list = self._room_npcs.get(old_room, [])
        if npc.id in room_list:
            room_list.remove(npc.id)
        npc.room_id           = new_room_id
        npc.current_room_id   = new_room_id
        self._room_npcs.setdefault(new_room_id, []).append(npc.id)

    # ── Query helpers ─────────────────────────────────────────────────────────

    def get_npcs_in_room(self, room_id: int) -> List[NPC]:
        return [self._npcs[nid] for nid in self._room_npcs.get(room_id, [])
                if nid in self._npcs]

    def find_npc_in_room(self, room_id: int, name_fragment: str) -> Optional[NPC]:
        name_lower = name_fragment.lower()
        for npc in self.get_npcs_in_room(room_id):
            if name_lower in npc.name.lower():
                return npc
        return None

    def get_shopkeeper_in_room(self, room_id: int) -> Optional[NPC]:
        for npc in self.get_npcs_in_room(room_id):
            if npc.can_shop and npc.shop_id:
                return npc
        return None

    def get_npc(self, npc_id: int) -> Optional[NPC]:
        return self._npcs.get(npc_id)

    def get_npc_by_template(self, template_id: str) -> Optional[NPC]:
        nid = self._template_to_id.get(template_id)
        return self._npcs.get(nid) if nid else None

    def get_service_npc_in_room(self, room_id: int, service_tag: str) -> Optional[NPC]:
        for npc in self.get_npcs_in_room(room_id):
            if npc.matches_service(service_tag):
                return npc
        return None

    def is_unkillable(self, npc_id: int) -> bool:
        npc = self._npcs.get(npc_id)
        return npc is not None and npc.unkillable

    def get_all_npcs(self) -> List[NPC]:
        return list(self._npcs.values())

    # ── Main tick ─────────────────────────────────────────────────────────────

    async def tick(self, tick_count: int):
        """Called every game tick (10/sec)."""

        # Ambient emotes + chat — every 5 seconds (50 ticks)
        if tick_count % 50 == 0:
            await self._emote_tick()
            await self._chat_tick()

        # Patrol movement — every 1 second (10 ticks)
        if tick_count % 10 == 0:
            await self._patrol_tick()
            await self._hook_tick()

        # Combat AI — every 1 second
        if tick_count % 10 == 0:
            await self._combat_tick()

        # Loot scan — every 10 seconds (100 ticks)
        if tick_count % 100 == 0:
            await self._loot_tick()

        # Bot AI — every 10 seconds
        if tick_count % 100 == 0:
            await self._bot_tick()

        # Respawn check — every 60 seconds (600 ticks)
        if tick_count % 600 == 0:
            await self._respawn_tick()

        # Guard shifts — every 60 seconds
        if tick_count % 600 == 0:
            await self._shift_tick()

    # ── Emote tick ────────────────────────────────────────────────────────────

    async def _emote_tick(self):
        for npc in list(self._npcs.values()):
            if not npc.can_emote:
                continue
            emote = npc.get_ambient_emote()
            if emote:
                await self.server.world.broadcast_to_room(npc.room_id, emote)

    # ── Chat tick ─────────────────────────────────────────────────────────────

    async def _chat_tick(self):
        for npc in list(self._npcs.values()):
            if not npc.can_chat:
                continue
            line = npc.get_chat_line()
            if line:
                await self.server.world.broadcast_to_room(npc.room_id, line)

    # ── Patrol tick ───────────────────────────────────────────────────────────

    async def _patrol_tick(self):
        for npc in list(self._npcs.values()):
            if not npc.can_wander or not npc.patrol_rooms:
                continue
            if not npc.is_ready_to_move():
                continue
            if random.random() > npc.wander_chance:
                npc.record_move()
                continue
            next_room = npc.get_next_patrol_room()
            if next_room and next_room != npc.room_id:
                await self._move_npc(npc, next_room)

    async def _hook_tick(self):
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        if not engine or not engine.available:
            return

        for npc in list(self._npcs.values()):
            if not npc.alive or not npc.has_hook("on_tick") or not npc._lua_table:
                continue
            try:
                engine.call_npc_hook(npc._lua_table, "on_tick")
            except Exception as e:
                log.error("NPC on_tick hook error (%s): %s", npc.template_id, e)

    async def _move_npc(self, npc: NPC, target_room_id: int):
        old_room  = npc.room_id
        direction = self._get_direction(old_room, target_room_id)

        if direction:
            depart_msg = npc_emote(
                f"{npc.display_name} {_DEPARTURE_BY_DIR.get(direction, 'heads off.')}"
            )
            arrive_msg = npc_emote(
                f"{npc.display_name} {_ARRIVAL_BY_DIR.get(direction, 'arrives.')}"
            )
        else:
            depart_msg = npc_emote(f"{npc.display_name} heads off.")
            arrive_msg = npc_emote(f"{npc.display_name} arrives.")

        tracker = getattr(self.server, "tracking", None)
        if tracker:
            try:
                tracker.record_departure(
                    actor_kind="npc",
                    actor_id=int(getattr(npc, "id", 0) or 0),
                    actor_name=getattr(npc, "display_name", None) or getattr(npc, "name", None) or "someone",
                    from_room_id=int(old_room),
                    to_room_id=int(target_room_id),
                    direction=direction or "out",
                    actor_level=int(getattr(npc, "level", 1) or 1),
                )
            except Exception as e:
                log.debug("Failed to record NPC trail: %s", e)

        self._move_npc_index(npc, target_room_id)
        npc.record_move()

        await self.server.world.broadcast_to_room(old_room,        depart_msg)
        await self.server.world.broadcast_to_room(target_room_id,  arrive_msg)

    def _get_direction(self, from_room: int, to_room: int) -> Optional[str]:
        try:
            world = self.server.world
            if hasattr(world, "get_direction_between"):
                return world.get_direction_between(from_room, to_room)
        except Exception:
            pass
        return None

    # ── Combat tick ───────────────────────────────────────────────────────────

    async def _combat_tick(self):
        """
        Combat-capable NPCs that are in_combat fire an attack via CombatEngine.
        Aggressive NPCs that are not in combat scan their room for targets.
        """
        combat = getattr(self.server, "combat", None)
        if not combat:
            return

        for npc in list(self._npcs.values()):
            if not npc.can_combat or not npc.alive:
                continue

            # In combat — attack target
            if npc.in_combat and npc.target:
                target = npc.target
                # Target may be a player session or a creature
                if getattr(target, "is_dead", False) or not getattr(target, "alive", True):
                    npc.in_combat = False
                    npc.target    = None
                    continue
                if npc.can_act():
                    try:
                        await combat.creature_attacks_player(npc, target)
                    except Exception as e:
                        log.error("NPC combat error (%s): %s", npc.template_id, e)

            # Aggressive and idle — scan for targets in the same room
            elif npc.aggressive and not npc.in_combat:
                players = self.server.world.get_players_in_room(npc.room_id)
                if players:
                    target = random.choice(players)
                    npc.in_combat = True
                    npc.target    = target
                    await self.server.world.broadcast_to_room(
                        npc.room_id,
                        colorize(
                            f"{npc.display_name} turns with hostile intent!",
                            TextPresets.COMBAT_DAMAGE_TAKEN
                        )
                    )

    # ── Loot tick ─────────────────────────────────────────────────────────────

    async def _loot_tick(self):
        """
        Loot-capable NPCs collect silver from dead creatures in their room.
        (Item/gem looting is a stub for the inventory system to hook into.)
        """
        creature_mgr = getattr(self.server, "creatures", None)
        if not creature_mgr:
            return

        for npc in list(self._npcs.values()):
            if not npc.can_loot or not npc.alive:
                continue

            dead = [c for c in creature_mgr.get_creatures_in_room(npc.room_id)
                    if c.is_dead and getattr(c, "treasure", {}).get("coins")]
            if not dead and npc.loot_radius > 0:
                # Check adjacent rooms if radius allows
                room = self.server.world.get_room(npc.room_id)
                if room:
                    for _, adj_id in list(room.exits.items())[:npc.loot_radius]:
                        dead += [c for c in creature_mgr.get_creatures_in_room(adj_id)
                                 if c.is_dead and getattr(c, "treasure", {}).get("coins")]

            for corpse in dead:
                # Collect silver — move it to the NPC (cosmetic for now)
                silver = getattr(corpse, "loot_silver", random.randint(1, 20))
                await self.server.world.broadcast_to_room(
                    npc.room_id,
                    npc_emote(
                        f"{npc.display_name} quickly pockets some silver from "
                        f"the remains of {getattr(corpse, 'full_name', 'a creature')}."
                    )
                )
                # Clear coin loot so no double-collect
                if hasattr(corpse, "treasure") and isinstance(corpse.treasure, dict):
                    corpse.treasure["coins"] = False

    # ── Bot tick ──────────────────────────────────────────────────────────────

    async def _bot_tick(self):
        """
        Bot NPCs: if injured below flee threshold, move toward rest room.
        Full bot hunting/shopping/chatting is a later stage.
        """
        for npc in list(self._npcs.values()):
            if not npc.is_bot or not npc.alive:
                continue

            hp_pct = npc.health_current / npc.health_max if npc.health_max > 0 else 1.0
            if hp_pct < npc.bot_hp_flee and npc.bot_rest_room and npc.room_id != npc.bot_rest_room:
                await self._move_npc_toward(npc, npc.bot_rest_room)

    async def _move_npc_toward(self, npc: NPC, target_room_id: int):
        """Move one step toward target_room_id using world pathfinding."""
        world = self.server.world
        if not hasattr(world, "find_path"):
            return
        path = world.find_path(npc.room_id, target_room_id)
        if path and len(path) >= 2:
            await self._move_npc(npc, path[1])

    # ── Respawn tick ──────────────────────────────────────────────────────────

    async def _respawn_tick(self):
        """Check dead NPCs and respawn those whose timer has expired."""
        now = time.time()
        for npc in list(self._npcs.values()):
            if npc.alive:
                continue
            if npc.respawn_seconds <= 0:
                continue
            if now - npc.death_time < npc.respawn_seconds:
                continue

            # Respawn
            npc.health_current = npc.health_max
            npc.alive          = True
            npc.is_alive       = True
            npc.in_combat      = False
            npc.target         = None
            npc.wounds         = {}
            npc.status_effects = {}
            npc.death_time     = 0.0

            # Return to home room
            if npc.room_id != npc.home_room_id:
                self._move_npc_index(npc, npc.home_room_id)

            await self.server.world.broadcast_to_room(
                npc.room_id,
                npc_emote(f"{npc.display_name} arrives.")
            )
            self._save_npc_state(npc)
            log.info("NPC respawned: %s in room %d", npc.template_id, npc.room_id)

    # ── Guard shift system ────────────────────────────────────────────────────

    def _register_shift_guard(self, template: dict, npc_instance: Optional[NPC]):
        sid   = template.get("shift_id")
        phase = int(template.get("shift_phase", 0))
        if not sid:
            return
        if sid not in self._shift_guards:
            self._shift_guards[sid] = {}
            self._shift_phase[sid]  = 0
        if npc_instance:
            self._shift_guards[sid][phase] = npc_instance.id
        else:
            self._shift_guards[sid][phase] = template

    async def _shift_tick(self):
        now = time.time()
        if now - self._last_shift_time < SHIFT_INTERVAL:
            return
        self._last_shift_time = now
        log.info("Guard shift change initiated.")
        for shift_id, guard_map in self._shift_guards.items():
            await self._do_shift_change(shift_id, guard_map)

    async def _do_shift_change(self, shift_id: str, guard_map: dict):
        current_phase  = self._shift_phase.get(shift_id, 0)
        incoming_phase = 1 - current_phase

        outgoing_entry = guard_map.get(current_phase)
        incoming_entry = guard_map.get(incoming_phase)
        if outgoing_entry is None or incoming_entry is None:
            return

        outgoing_npc = (self._npcs.get(outgoing_entry)
                        if isinstance(outgoing_entry, int) else None)

        if isinstance(incoming_entry, int):
            incoming_npc = self._npcs.get(incoming_entry)
        elif isinstance(incoming_entry, dict):
            incoming_npc = NPC(incoming_entry)
            if outgoing_npc:
                incoming_npc.room_id      = outgoing_npc.room_id
                incoming_npc.home_room_id = outgoing_npc.home_room_id
            self._place_npc(incoming_npc)
            guard_map[incoming_phase] = incoming_npc.id
        else:
            incoming_npc = None

        if not outgoing_npc or not incoming_npc:
            return

        gate_room = outgoing_npc.room_id

        depart_lines = _SHIFT_DEPARTURE_LINES.get(shift_id, ["{name} departs."])
        arrive_lines = _SHIFT_ARRIVAL_LINES.get(shift_id,  ["{name} arrives."])
        depart_msg = npc_emote(random.choice(depart_lines).replace("{name}", outgoing_npc.name))
        arrive_msg = npc_emote(random.choice(arrive_lines).replace("{name}", incoming_npc.name))

        await self.server.world.broadcast_to_room(gate_room, depart_msg)
        self._remove_npc(outgoing_npc)

        self._move_npc_index(incoming_npc, gate_room)
        await self.server.world.broadcast_to_room(gate_room, arrive_msg)

        self._shift_phase[shift_id] = incoming_phase
        log.info("Shift change at %s gate: %s out, %s in.",
                 shift_id, outgoing_npc.name, incoming_npc.name)

    # ── Event hooks ───────────────────────────────────────────────────────────

    async def on_player_enter_room(self, session, room_id: int):
        """Called by movement handler when a player enters a room."""
        for npc in self.get_npcs_in_room(room_id):
            # Greeting
            greeting_text = npc.get_greeting_text()
            if greeting_text:
                greeting = greeting_text.replace("{player}", session.character_name)
                await session.send_line(npc_emote(f"{npc.display_name} {greeting}"))

            # Lua hook: on_player_enter
            if npc.has_hook("on_player_enter") and npc._lua_table:
                try:
                    lua = getattr(self.server, "lua", None)
                    engine = getattr(lua, "engine", None) if lua else None
                    if engine and engine.available:
                        engine.call_npc_hook(npc._lua_table, "on_player_enter", session)
                except Exception as e:
                    log.error("NPC on_player_enter hook error (%s): %s",
                              npc.template_id, e)

    async def on_npc_death(self, npc: NPC, killer=None):
        """
        Called when an NPC is killed (by player or creature).
        Handles loot drop, death message, state save, hook.
        """
        npc.alive    = False
        npc.is_alive = False
        npc.in_combat = False
        npc.target    = None
        npc.death_time = time.time()
        npc.status_effects = {}

        await self.server.world.broadcast_to_room(
            npc.room_id,
            colorize(
                f"  {npc.display_name} collapses lifelessly.",
                TextPresets.COMBAT_DEATH
            )
        )

        # Lua hook: on_death
        if npc.has_hook("on_death") and npc._lua_table:
            try:
                lua    = getattr(self.server, "lua", None)
                engine = getattr(lua, "engine", None) if lua else None
                if engine and engine.available:
                    engine.call_npc_hook(npc._lua_table, "on_death")
            except Exception as e:
                log.error("NPC on_death hook error (%s): %s", npc.template_id, e)

        self._save_npc_state(npc)

    async def fire_invasion_hook(self, zone_slug: str):
        """Called by the invasion manager when an invasion begins in a zone."""
        for npc in list(self._npcs.values()):
            if not npc.is_invasion:
                continue
            if npc.invasion_zone and npc.invasion_zone != zone_slug:
                continue
            if npc.has_hook("on_invasion") and npc._lua_table:
                try:
                    lua    = getattr(self.server, "lua", None)
                    engine = getattr(lua, "engine", None) if lua else None
                    if engine and engine.available:
                        engine.call_npc_hook(npc._lua_table, "on_invasion", zone_slug)
                except Exception as e:
                    log.error("NPC on_invasion hook error (%s): %s", npc.template_id, e)

    # ── Player flag helpers (quest / relationship state) ──────────────────────

    def get_player_flag(self, template_id: str, character_id: int, flag: str) -> str:
        """Read a per-player flag from the DB. Returns '' if not set."""
        db = getattr(self.server, "db", None)
        if not db:
            return ""
        try:
            conn = db._get_conn()
            cur  = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT flag_value FROM npc_player_flags "
                "WHERE template_id=%s AND character_id=%s AND flag_name=%s",
                (template_id, character_id, flag)
            )
            row = cur.fetchone()
            conn.close()
            return row["flag_value"] if row else ""
        except Exception:
            return ""

    def set_player_flag(self, template_id: str, character_id: int, flag: str, value: str):
        """Write a per-player flag to the DB."""
        db = getattr(self.server, "db", None)
        if not db:
            return
        try:
            db.execute_update(
                """INSERT INTO npc_player_flags (template_id, character_id, flag_name, flag_value)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE flag_value=VALUES(flag_value)""",
                (template_id, character_id, flag, value)
            )
        except Exception as e:
            log.warning("set_player_flag failed (%s/%s/%s): %s",
                        template_id, character_id, flag, e)
