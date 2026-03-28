"""
pet_manager.py
--------------
Dedicated companion runtime for the GemStone IV private server.

Pets are not creatures, not NPCs, and not hidden status flags. They are
owner-bound companion entities with their own persistence, progression,
abilities, website shop flow, and room presence rules.
"""

from __future__ import annotations

import logging
import random
import re
import time
from typing import Dict, List, Optional

from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)


class PetManager:
    """Central owner for pet data, runtime state, and pet-specific hooks."""

    def __init__(self, server):
        self.server = server
        self.cfg: dict = {}
        self._outside_room_map: dict[int, dict] = {}
        self._pet_room_map: dict[int, dict] = {}

    async def initialize(self):
        cfg = getattr(self.server.lua, "get_pets", lambda: None)()
        if not isinstance(cfg, dict) or not cfg:
            raise RuntimeError("PetManager: pets.lua failed to load or returned empty data")
        self.cfg = cfg
        self._outside_room_map = {}
        self._pet_room_map = {}
        for city_key, entry in ((cfg.get("system") or {}).get("city_shops") or {}).items():
            if not isinstance(entry, dict):
                continue
            outside_room_id = int(entry.get("outside_room_id") or 0)
            pet_room_id = int(entry.get("pet_room_id") or 0)
            if outside_room_id:
                self._outside_room_map[outside_room_id] = {"city_key": city_key, **entry}
            if pet_room_id:
                self._pet_room_map[pet_room_id] = {"city_key": city_key, **entry}
        log.info(
            "PetManager ready (%d species, %d city shop paths)",
            len((cfg.get("species") or {})),
            len(self._outside_room_map),
        )

    # ------------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------------

    def _now(self) -> int:
        return int(time.time())

    def system_cfg(self) -> dict:
        return self.cfg.get("system") or {}

    def species_cfg(self, species_key: str) -> dict:
        return ((self.cfg.get("species") or {}).get(species_key) or {})

    def get_xp_curve(self) -> list:
        curve = self.cfg.get("xp_curve") or []
        return [row for row in curve if isinstance(row, dict)]

    def get_max_level(self) -> int:
        return int((self.system_cfg().get("max_pet_level") or 50))

    def is_pet_shop_room(self, room_id: int) -> bool:
        try:
            return int(room_id) in self._pet_room_map
        except Exception:
            return False

    def city_shop_for_room(self, room_id: int) -> Optional[dict]:
        try:
            room_id = int(room_id)
        except Exception:
            return None
        return self._pet_room_map.get(room_id) or self._outside_room_map.get(room_id)

    def shop_entry_display(self) -> str:
        return str(self.system_cfg().get("shop_entry_display") or "menagerie")

    def shop_entry_key(self) -> str:
        return str(self.system_cfg().get("shop_entry_exit_key") or "go_menagerie")

    def get_dynamic_room_exits(self, session, room) -> Dict[str, int]:
        if not session or not room:
            return {}
        progress = getattr(session, "pet_progress", {}) or {}
        if not progress.get("path_unlocked"):
            return {}
        city = self._outside_room_map.get(int(getattr(room, "id", 0) or 0))
        if not city:
            return {}
        return {self.shop_entry_key(): int(city["pet_room_id"])}

    def is_companion_hidden(self, session, pet: Optional[dict] = None) -> bool:
        if not session:
            return True
        if getattr(session, "is_dead", False):
            return True
        if getattr(session, "hidden", False) or getattr(session, "sneaking", False):
            return True
        if pet and (pet.get("is_released") or (pet.get("extra_state") or {}).get("dismissed")):
            return True
        return False

    # ------------------------------------------------------------------
    # Persistence loading / saving
    # ------------------------------------------------------------------

    def _normalize_progress(self, row: dict | None) -> dict:
        row = dict(row or {})
        accepted_at = row.get("accepted_at")
        completed_at = row.get("completed_at")
        if hasattr(accepted_at, "isoformat"):
            accepted_at = accepted_at.isoformat(sep=" ")
        if hasattr(completed_at, "isoformat"):
            completed_at = completed_at.isoformat(sep=" ")
        return {
            "character_id": int(row.get("character_id") or 0),
            "quest_state": row.get("quest_state") or "locked",
            "sprite_name": row.get("sprite_name") or "Twillip",
            "first_pet_claimed": bool(row.get("first_pet_claimed")),
            "path_unlocked": bool(row.get("path_unlocked")),
            "active_pet_id": int(row.get("active_pet_id") or 0) or None,
            "last_sprite_nag_at": int(row.get("last_sprite_nag_at") or 0),
            "last_shop_nag_at": int(row.get("last_shop_nag_at") or 0),
            "room_moves_since_nag": int(row.get("room_moves_since_nag") or 0),
            "accepted_at": accepted_at,
            "completed_at": completed_at,
        }

    def _normalize_pet(self, row: dict) -> dict:
        row = dict(row or {})
        row["id"] = int(row.get("id") or 0)
        row["character_id"] = int(row.get("character_id") or 0)
        row["pet_level"] = int(row.get("pet_level") or 1)
        row["pet_xp"] = int(row.get("pet_xp") or 0)
        row["is_active"] = bool(row.get("is_active"))
        row["is_deleted"] = bool(row.get("is_deleted"))
        row["is_released"] = bool(row.get("is_released"))
        row["last_fed_at"] = int(row.get("last_fed_at") or 0)
        row["last_random_emote_at"] = int(row.get("last_random_emote_at") or 0)
        row["last_state_emote_at"] = int(row.get("last_state_emote_at") or 0)
        row["extra_state"] = dict(row.get("extra_state") or {})
        row["abilities"] = {}
        row["equipment"] = {}
        return row

    def _save_progress(self, session):
        if getattr(self.server, "db", None) and getattr(session, "character_id", None):
            self.server.db.save_pet_progress(session.character_id, session.pet_progress)

    def _save_pet(self, pet: dict):
        if getattr(self.server, "db", None):
            self.server.db.save_character_pet(pet)

    def _save_pet_ability(self, pet: dict, ability_key: str):
        db = getattr(self.server, "db", None)
        if not db:
            return
        state = (pet.get("abilities") or {}).get(ability_key) or {}
        db.upsert_pet_ability_state(
            pet["id"],
            ability_key,
            charges_current=state.get("charges_current", 0),
            cooldown_until=state.get("cooldown_until", 0),
            last_triggered_at=state.get("last_triggered_at", 0),
            extra_state=state.get("extra_state", {}),
        )

    def _load_pet_abilities(self, pet: dict):
        db = getattr(self.server, "db", None)
        if not db or not pet.get("id"):
            return
        pet["abilities"] = db.load_pet_ability_state(pet["id"]) or {}
        pet["equipment"] = db.load_pet_equipment(pet["id"]) or {}

    def _refresh_pet_reference(self, session):
        active = None
        active_pet_id = (getattr(session, "pet_progress", {}) or {}).get("active_pet_id")
        for pet in getattr(session, "pets", []) or []:
            if pet.get("id") == active_pet_id or pet.get("is_active"):
                active = pet
                break
        if active:
            active["is_active"] = True
            session.pet_progress["active_pet_id"] = active["id"]
        session.active_pet = active

    async def load_for_session(self, session):
        db = getattr(self.server, "db", None)
        if not db or not getattr(session, "character_id", None):
            session.pet_progress = self._normalize_progress({})
            session.pets = []
            session.active_pet = None
            session.pet_sprite_visible = False
            return

        session.pet_progress = self._normalize_progress(
            db.get_or_create_pet_progress(session.character_id)
        )
        raw_pets = db.load_character_pets(session.character_id) or []
        session.pets = [self._normalize_pet(row) for row in raw_pets]
        for pet in session.pets:
            self._load_pet_abilities(pet)
        self._refresh_pet_reference(session)

        if int(getattr(session, "level", 1) or 1) >= 5 and session.pet_progress.get("quest_state") == "locked":
            await self.offer_quest(session, announce=False)

        if session.pet_progress.get("quest_state") in {"offered", "accepted"} and not session.pet_progress.get("first_pet_claimed"):
            session.pet_sprite_visible = True
        else:
            session.pet_sprite_visible = False

    async def on_login(self, session):
        await self.load_for_session(session)
        if session.pet_progress.get("quest_state") == "offered":
            await self._send_lines(session, self.cfg.get("quest", {}).get("intro_lines") or [])

    async def on_level_up(self, session, old_level: int, new_level: int):
        if old_level < 5 <= new_level:
            await self.offer_quest(session, announce=True)

    async def offer_quest(self, session, announce: bool = True):
        progress = getattr(session, "pet_progress", {}) or {}
        if progress.get("quest_state") not in {"locked", ""}:
            return
        progress["quest_state"] = "offered"
        progress["sprite_name"] = self.cfg.get("quest", {}).get("sprite_name") or self.system_cfg().get("sprite_name") or "Twillip"
        progress["path_unlocked"] = False
        progress["first_pet_claimed"] = False
        progress["room_moves_since_nag"] = 0
        session.pet_progress = progress
        session.pet_sprite_visible = True
        self._save_progress(session)
        if announce:
            await self._send_lines(session, self.cfg.get("quest", {}).get("intro_lines") or [])

    async def handle_accept(self, session) -> bool:
        progress = getattr(session, "pet_progress", {}) or {}
        if progress.get("quest_state") != "offered":
            return False
        progress["quest_state"] = "accepted"
        progress["path_unlocked"] = True
        progress["accepted_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        progress["room_moves_since_nag"] = 0
        progress["last_shop_nag_at"] = self._now()
        session.pet_progress = progress
        session.pet_sprite_visible = True
        self._save_progress(session)
        await self._send_lines(session, self.cfg.get("quest", {}).get("accept_lines") or [])
        return True

    async def complete_first_pet_quest(self, session):
        progress = getattr(session, "pet_progress", {}) or {}
        progress["quest_state"] = "completed"
        progress["first_pet_claimed"] = True
        progress["path_unlocked"] = True
        progress["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        session.pet_progress = progress
        session.pet_sprite_visible = False
        self._save_progress(session)
        await self._send_lines(session, self.cfg.get("quest", {}).get("completion_lines") or [])

    # ------------------------------------------------------------------
    # World presence
    # ------------------------------------------------------------------

    def get_visible_entities_in_room(self, room_id: int, *, viewer=None) -> List[dict]:
        room_id = int(room_id or 0)
        entities: list[dict] = []
        for session in self.server.sessions.playing():
            current_room = getattr(getattr(session, "current_room", None), "id", 0)
            if int(current_room or 0) != room_id:
                continue
            if getattr(session, "pet_sprite_visible", False):
                entities.append({
                    "kind": "sprite",
                    "owner": session,
                    "name": (session.pet_progress or {}).get("sprite_name") or "Twillip",
                    "display_name": (session.pet_progress or {}).get("sprite_name") or "Twillip",
                })
            pet = getattr(session, "active_pet", None)
            if pet and not self.is_companion_hidden(session, pet):
                species = self.species_cfg(pet.get("species_key"))
                entities.append({
                    "kind": "pet",
                    "owner": session,
                    "pet": pet,
                    "species": species,
                    "name": pet.get("pet_name") or species.get("race_name") or "companion",
                    "display_name": f"{pet.get('pet_name')} the {species.get('race_name', 'companion')}",
                })
        return entities

    def find_visible_entity(self, room_id: int, target: str, *, viewer=None) -> Optional[dict]:
        target = (target or "").strip().lower()
        if not target:
            return None
        for entity in self.get_visible_entities_in_room(room_id, viewer=viewer):
            owner = entity.get("owner")
            names = {
                (entity.get("name") or "").lower(),
                (entity.get("display_name") or "").lower(),
                ((entity.get("species") or {}).get("race_name") or "").lower(),
                ((owner.character_name if owner else "") or "").lower(),
            }
            if entity["kind"] == "sprite":
                names.update({"sprite", "guide"})
            else:
                names.add("pet")
                if owner and owner.character_name:
                    names.add(f"{owner.character_name.lower()}'s pet")
            names = {n for n in names if n}
            if any(target == n or target in n for n in names):
                return entity
        return None

    def format_room_line(self, entity: dict) -> str:
        if entity["kind"] == "sprite":
            owner = entity.get("owner")
            if owner:
                return f'You also see {entity["display_name"]}, a tiny prismatic sprite hovering near {owner.character_name}.'
            return f'You also see {entity["display_name"]}, a tiny prismatic sprite.'
        owner = entity.get("owner")
        pet = entity.get("pet") or {}
        species = entity.get("species") or {}
        if owner:
            return (
                f"You also see {pet.get('pet_name')} the {species.get('race_name', 'companion')} "
                f"following {owner.character_name}."
            )
        return f'You also see {pet.get("pet_name")} here.'

    def look_lines_for_entity(self, entity: dict) -> List[str]:
        if entity["kind"] == "sprite":
            owner = entity.get("owner")
            lines = [
                f'You see {entity["display_name"]}, a tiny prismatic sprite with glittering wings and a thoroughly determined expression.',
            ]
            if owner:
                lines.append(f'  She appears fixated on {owner.character_name} and looks entirely unwilling to leave them alone.')
            lines.append('  She is here to guide eligible adventurers toward the Moonwhisker Menagerie.')
            return lines

        owner = entity.get("owner")
        pet = entity.get("pet") or {}
        species = entity.get("species") or {}
        lines = [
            f'You see {pet.get("pet_name")} the {species.get("race_name", "companion")}.',
        ]
        for line in species.get("appearance_lines") or []:
            lines.append(f"  {line}")
        if owner:
            lines.append(f'  {pet.get("pet_name")} belongs to {owner.character_name}.')
        lines.append(f'  Level {int(pet.get("pet_level") or 1)} companion.')
        for ability_key, ability in (species.get("abilities") or {}).items():
            lines.append(f'  {ability.get("label", ability_key)}: {ability.get("description", "")}')
        return lines

    def move_messages(self, session, direction: str, sneaking: bool) -> tuple[Optional[str], Optional[str]]:
        pet = getattr(session, "active_pet", None)
        if not pet or self.is_companion_hidden(session, pet):
            return None, None
        pet_name = pet.get("pet_name") or "a companion"
        if sneaking:
            return (
                f"{session.character_name} slips away silently, with {pet_name} ghosting after in perfect mimicry.",
                f"Something shifts in the shadows, followed by the faintest sparkle of {pet_name}.",
            )
        dir_text = str(direction or "away").replace("_", " ")
        return (
            f"{session.character_name} just went {dir_text} with {pet_name} happily following in tow.",
            f"{session.character_name} just arrived with {pet_name} close at heel.",
        )

    async def on_room_enter(self, session, from_room, to_room):
        progress = getattr(session, "pet_progress", {}) or {}
        if progress.get("quest_state") == "offered" and not progress.get("first_pet_claimed"):
            progress["room_moves_since_nag"] = int(progress.get("room_moves_since_nag") or 0) + 1
            session.pet_progress = progress
            self._save_progress(session)
            return
        if (
            progress.get("quest_state") == "accepted"
            and not progress.get("first_pet_claimed")
            and to_room
            and self.is_pet_shop_room(getattr(to_room, "id", 0))
        ):
            progress["last_shop_nag_at"] = self._now()
            session.pet_progress = progress
            self._save_progress(session)
            await session.send_line(colorize(
                random.choice(self.cfg.get("quest", {}).get("shop_arrival_lines") or ["Use PET SHOP to open the companion catalogue."]),
                TextPresets.NPC_SPEECH,
            ))

    # ------------------------------------------------------------------
    # Tick / emotes / pet spells
    # ------------------------------------------------------------------

    async def tick(self, tick_count: int):
        if tick_count % 10 != 0:
            return
        now = self._now()
        for session in self.server.sessions.playing():
            try:
                await self._tick_session(session, now)
            except Exception as e:
                log.error("PetManager tick error for %s: %s", getattr(session, "character_name", "unknown"), e, exc_info=True)

    async def _tick_session(self, session, now: int):
        progress = getattr(session, "pet_progress", {}) or {}
        if not progress:
            return
        if progress.get("quest_state") == "offered" and not progress.get("first_pet_claimed"):
            interval = int(self.system_cfg().get("sprite_nag_room_interval") or 5)
            if int(progress.get("room_moves_since_nag") or 0) >= interval:
                progress["room_moves_since_nag"] = 0
                progress["last_sprite_nag_at"] = now
                session.pet_progress = progress
                self._save_progress(session)
                await session.send_line(colorize(
                    random.choice(self.cfg.get("quest", {}).get("reminder_lines") or ["Type ACCEPT to begin the pet quest."]),
                    TextPresets.NPC_SPEECH,
                ))
        elif progress.get("quest_state") == "accepted" and not progress.get("first_pet_claimed"):
            if now - int(progress.get("last_shop_nag_at") or 0) >= int(self.system_cfg().get("sprite_nag_seconds") or 600):
                progress["last_shop_nag_at"] = now
                session.pet_progress = progress
                self._save_progress(session)
                in_pet_shop = bool(getattr(session, "current_room", None) and self.is_pet_shop_room(session.current_room.id))
                nag_lines = (
                    self.cfg.get("quest", {}).get("shop_reminder_lines")
                    if in_pet_shop
                    else self.cfg.get("quest", {}).get("accepted_nag_lines")
                ) or ["Visit Moonwhisker Menagerie for your first companion."]
                await session.send_line(colorize(
                    random.choice(nag_lines),
                    TextPresets.NPC_SPEECH,
                ))

        pet = getattr(session, "active_pet", None)
        if not pet or pet.get("is_released"):
            return

        await self._maybe_emit_pet_emote(session, pet, now)
        await self._maybe_cast_pet_regen(session, pet, now)

    async def _maybe_emit_pet_emote(self, session, pet: dict, now: int):
        species = self.species_cfg(pet.get("species_key"))
        if not species:
            return
        personality = species.get("personality") or {}
        state_emotes = (personality.get("state_emotes") or {})
        random_emotes = personality.get("random_emotes") or []

        treat_ready = False
        if int(pet.get("last_fed_at") or 0):
            treat_ready = (now - int(pet.get("last_fed_at") or 0)) >= int(self.system_cfg().get("feed_cooldown_seconds") or 7200)
        elif session.pet_progress.get("first_pet_claimed"):
            treat_ready = True

        state_pool = []
        hp_pct = (float(getattr(session, "health_current", 0) or 0) / max(1.0, float(getattr(session, "health_max", 1) or 1)))
        if hp_pct < 0.60:
            state_pool.extend(state_emotes.get("low_health") or [])
        elif hp_pct > 0.85:
            state_pool.extend(state_emotes.get("recovered") or [])
        if treat_ready:
            state_pool.extend(state_emotes.get("treat_ready") or [])

        if state_pool and (now - int(pet.get("last_state_emote_at") or 0) >= 180):
            text = random.choice(state_pool)
            pet["last_state_emote_at"] = now
            self._save_pet(pet)
            await self._broadcast_pet_emote(session, pet, text)
            return

        if random_emotes and (now - int(pet.get("last_random_emote_at") or 0) >= 240):
            if random.random() <= 0.35:
                text = random.choice(random_emotes)
                pet["last_random_emote_at"] = now
                self._save_pet(pet)
                await self._broadcast_pet_emote(session, pet, text)

    async def _broadcast_pet_emote(self, session, pet: dict, template: str):
        room = getattr(session, "current_room", None)
        if not room or self.is_companion_hidden(session, pet):
            return
        text = template.format(
            pet=pet.get("pet_name") or "The companion",
            owner=session.character_name or "its owner",
        )
        await self.server.world.broadcast_to_room(room.id, text)

    def _ability_scaling_for_level(self, species_key: str, ability_key: str, pet_level: int) -> dict:
        species = self.species_cfg(species_key)
        ability = ((species.get("abilities") or {}).get(ability_key) or {})
        scaling = ability.get("scaling") or []
        if isinstance(scaling, list) and scaling:
            idx = max(0, min(len(scaling) - 1, int(pet_level or 1) - 1))
            return scaling[idx] if isinstance(scaling[idx], dict) else {}
        return {}

    def _ensure_ability_state(self, pet: dict, ability_key: str) -> dict:
        abilities = pet.setdefault("abilities", {})
        state = abilities.get(ability_key)
        if not state:
            state = {
                "ability_key": ability_key,
                "charges_current": 0,
                "cooldown_until": 0,
                "last_triggered_at": 0,
                "extra_state": {},
            }
            abilities[ability_key] = state
        return state

    def _refresh_charge_window(self, pet: dict, ability_key: str, *, now: Optional[int] = None):
        now = now or self._now()
        state = self._ensure_ability_state(pet, ability_key)
        scaling = self._ability_scaling_for_level(pet.get("species_key"), ability_key, pet.get("pet_level"))
        max_charges = int(scaling.get("charges") or 0)
        cooldown = int(scaling.get("cooldown_seconds") or 0)
        if max_charges <= 0:
            return state
        if int(state.get("charges_current") or 0) <= 0 and int(state.get("cooldown_until") or 0) and now >= int(state.get("cooldown_until") or 0):
            state["charges_current"] = max_charges
            state["cooldown_until"] = 0
            self._save_pet_ability(pet, ability_key)
        elif int(state.get("charges_current") or 0) <= 0 and not int(state.get("cooldown_until") or 0):
            state["charges_current"] = max_charges
            if cooldown > 0:
                self._save_pet_ability(pet, ability_key)
        return state

    def _format_duration_short(self, seconds: int) -> str:
        seconds = max(0, int(seconds or 0))
        if seconds < 60:
            return f"{seconds}s"
        minutes, sec = divmod(seconds, 60)
        if minutes < 60:
            return f"{minutes}m" if sec == 0 else f"{minutes}m {sec}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h" if minutes == 0 else f"{hours}h {minutes}m"

    def _ability_unlock_level(self, ability: dict) -> int:
        for row in ability.get("scaling") or []:
            if isinstance(row, dict) and row.get("unlocked"):
                return int(row.get("level") or 1)
        return 1

    def _ability_summary_text(self, ability_key: str, scaling: dict, *, locked: bool = False) -> str:
        if locked:
            unlock_level = int(scaling.get("level") or 1)
            return f"Unlocks at level {unlock_level}."
        if ability_key == "guardian_spark":
            charges = int(scaling.get("charges") or 0)
            cooldown = self._format_duration_short(int(scaling.get("cooldown_seconds") or 0))
            return f"Prevents death and leaves the owner at 1 HP. Restores {charges} charge{'s' if charges != 1 else ''} every {cooldown}."
        if ability_key == "comforting_glow":
            heal_pct = float(scaling.get("heal_pct") or 0.0) * 100.0
            tick = self._format_duration_short(int(scaling.get("tick_interval") or 0))
            duration = self._format_duration_short(int(scaling.get("duration_seconds") or 0))
            recast = self._format_duration_short(int(scaling.get("recast_seconds") or 0))
            threshold = int(round(float(scaling.get("threshold_pct") or 0.0) * 100.0))
            return f"Heals {heal_pct:.1f}% HP every {tick} for {duration} when the owner falls below {threshold}% HP. Recasts every {recast}."
        if ability_key == "starlight_recall":
            revive_pct = float(scaling.get("revive_health_pct") or 0.0) * 100.0
            cooldown = self._format_duration_short(int(scaling.get("cooldown_seconds") or 0))
            return f"Revives the owner in place at {revive_pct:.0f}% HP once every {cooldown}."
        return ""

    def _ability_status_text(self, session, pet: dict, ability_key: str, state: dict, scaling: dict) -> str:
        now = self._now()
        cooldown_remaining = max(0, int(state.get("cooldown_until") or 0) - now)
        if ability_key == "guardian_spark":
            charges_current = int(state.get("charges_current") or 0)
            charges_max = int(scaling.get("charges") or 0)
            if cooldown_remaining > 0 and charges_current <= 0:
                return f"Recharging: {self._format_duration_short(cooldown_remaining)} remaining"
            return f"Ready: {charges_current}/{charges_max} charge{'s' if charges_max != 1 else ''}"
        if ability_key == "comforting_glow":
            if getattr(session, "active_pet", None) is pet and getattr(self.server, "status", None) and self.server.status.has(session, "floofer_glow"):
                return "Active on owner"
            if cooldown_remaining > 0:
                return f"Recast: {self._format_duration_short(cooldown_remaining)} remaining"
            return "Ready to cast"
        if ability_key == "starlight_recall":
            if not scaling.get("unlocked"):
                return f"Locked until level {self._ability_unlock_level((self.species_cfg(pet.get('species_key')).get('abilities') or {}).get(ability_key) or {})}"
            if cooldown_remaining > 0:
                return f"Recharging: {self._format_duration_short(cooldown_remaining)} remaining"
            return "Ready"
        return "Ready"

    def _build_portal_ability(self, session, pet: Optional[dict], species_key: str, ability_key: str, level: int) -> dict:
        species = self.species_cfg(species_key)
        ability = ((species.get("abilities") or {}).get(ability_key) or {})
        scaling = self._ability_scaling_for_level(species_key, ability_key, level)
        unlock_level = self._ability_unlock_level(ability)
        locked = bool(level < unlock_level or (ability_key == "starlight_recall" and not scaling.get("unlocked")))
        if pet:
            state = self._ensure_ability_state(pet, ability_key)
            if "charges" in scaling:
                state = self._refresh_charge_window(pet, ability_key)
        else:
            state = {"charges_current": int(scaling.get("charges") or 0), "cooldown_until": 0}

        next_level = min(self.get_max_level(), max(1, int(level or 1)) + 1)
        next_scaling = self._ability_scaling_for_level(species_key, ability_key, next_level)
        next_locked = bool(next_level < unlock_level or (ability_key == "starlight_recall" and not next_scaling.get("unlocked")))

        return {
            "key": ability_key,
            "label": ability.get("label", ability_key),
            "description": ability.get("description", ""),
            "unlock_level": unlock_level,
            "locked": locked,
            "status": self._ability_status_text(session, pet, ability_key, state, scaling) if pet else ("Locked until level %d" % unlock_level if locked else "Available at purchase"),
            "current_level": int(level or 1),
            "current_summary": self._ability_summary_text(ability_key, scaling if not locked else {"level": unlock_level}, locked=locked),
            "next_level": next_level if next_level > int(level or 1) else None,
            "next_summary": self._ability_summary_text(ability_key, next_scaling if not next_locked else {"level": unlock_level}, locked=next_locked) if next_level > int(level or 1) else "",
        }

    async def _maybe_cast_pet_regen(self, session, pet: dict, now: int):
        if getattr(session, "is_dead", False):
            return
        if self.is_companion_hidden(session, pet):
            return
        species = self.species_cfg(pet.get("species_key"))
        if pet.get("species_key") != "floofer" or not species:
            return

        scaling = self._ability_scaling_for_level("floofer", "comforting_glow", pet.get("pet_level"))
        state = self._ensure_ability_state(pet, "comforting_glow")
        threshold = float(scaling.get("threshold_pct") or 0.60)
        hp_pct = (float(getattr(session, "health_current", 0) or 0) / max(1.0, float(getattr(session, "health_max", 1) or 1)))
        if hp_pct >= threshold:
            return
        if self.server.status.has(session, "floofer_glow"):
            return
        if int(state.get("cooldown_until") or 0) > now:
            return

        self.server.status.apply(
            session,
            "floofer_glow",
            duration=float(scaling.get("duration_seconds") or 60),
            magnitude=float(scaling.get("heal_pct") or 0.01),
            source=pet.get("pet_name"),
            owner_pet_id=pet.get("id"),
            heal_pct=float(scaling.get("heal_pct") or 0.01),
        )
        state["last_triggered_at"] = now
        state["cooldown_until"] = now + int(scaling.get("recast_seconds") or 180)
        self._save_pet_ability(pet, "comforting_glow")

    # ------------------------------------------------------------------
    # Death / revival hooks
    # ------------------------------------------------------------------

    async def before_owner_death(self, session, killer=None) -> bool:
        pet = getattr(session, "active_pet", None)
        if not pet or pet.get("species_key") != "floofer" or pet.get("is_released"):
            return False
        now = self._now()

        guardian_state = self._refresh_charge_window(pet, "guardian_spark", now=now)
        guardian_scaling = self._ability_scaling_for_level("floofer", "guardian_spark", pet.get("pet_level"))
        if int(guardian_state.get("charges_current") or 0) > 0:
            guardian_state["charges_current"] = int(guardian_state.get("charges_current") or 0) - 1
            guardian_state["last_triggered_at"] = now
            if int(guardian_state.get("charges_current") or 0) <= 0:
                guardian_state["cooldown_until"] = now + int(guardian_scaling.get("cooldown_seconds") or 10800)
            self._save_pet_ability(pet, "guardian_spark")
            session.health_current = 1
            await session.send_line(colorize(
                f"  {pet.get('pet_name')} erupts in a desperate halo of sparks and drags you back from the brink of death!",
                TextPresets.EXPERIENCE,
            ))
            if session.current_room:
                await self.server.world.broadcast_to_room(
                    session.current_room.id,
                    colorize(
                        f"  {pet.get('pet_name')} bursts with protective starlight around {session.character_name}, refusing to let them fall.",
                        TextPresets.EXPERIENCE,
                    ),
                    exclude=session,
                )
            if self.server.db and session.character_id:
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current, session.mana_current,
                    session.spirit_current, session.stamina_current,
                    session.silver,
                )
            return True

        recall_scaling = self._ability_scaling_for_level("floofer", "starlight_recall", pet.get("pet_level"))
        if not recall_scaling.get("unlocked"):
            return False
        recall_state = self._ensure_ability_state(pet, "starlight_recall")
        if int(recall_state.get("cooldown_until") or 0) > now:
            return False

        recall_state["last_triggered_at"] = now
        recall_state["cooldown_until"] = now + int(recall_scaling.get("cooldown_seconds") or 3600)
        self._save_pet_ability(pet, "starlight_recall")
        revived_hp = max(1, int((float(getattr(session, "health_max", 1) or 1) * float(recall_scaling.get("revive_health_pct") or 0.10))))
        session.health_current = revived_hp
        await session.send_line(colorize(
            f"  As death closes in, {pet.get('pet_name')} refuses to flee.  A veil of starlight folds around you and you lurch back to life!",
            TextPresets.EXPERIENCE,
        ))
        if session.current_room:
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                colorize(
                    f"  {pet.get('pet_name')} lingers beside {session.character_name}, weaving a desperate lattice of starlight that hauls them back from death.",
                    TextPresets.EXPERIENCE,
                ),
                exclude=session,
            )
        if self.server.db and session.character_id:
            self.server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver,
            )
        return True

    async def on_owner_death(self, session):
        pet = getattr(session, "active_pet", None)
        if not pet or pet.get("is_released"):
            return
        if session.current_room:
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"{pet.get('pet_name')} lets out a thin, panicked trill and darts away from the scene.",
            )

    async def on_owner_revived(self, session):
        pet = getattr(session, "active_pet", None)
        if not pet or pet.get("is_released"):
            return
        if session.current_room:
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"{pet.get('pet_name')} returns in a flutter of relieved sparkles and hurries back to {session.character_name}.",
                exclude=None,
            )

    # ------------------------------------------------------------------
    # Commands / interactions
    # ------------------------------------------------------------------

    async def cmd_status(self, session):
        pet = getattr(session, "active_pet", None)
        progress = getattr(session, "pet_progress", {}) or {}
        if not pet:
            await session.send_line("You do not currently have an active companion.")
            if progress.get("quest_state") == "offered":
                await session.send_line("Twillip is still waiting for you to ACCEPT the pet quest.")
            elif progress.get("quest_state") == "accepted" and not progress.get("first_pet_claimed"):
                await session.send_line("Moonwhisker Menagerie is waiting for you to claim your first free pet.")
            return
        species = self.species_cfg(pet.get("species_key"))
        curve = self.get_xp_curve()
        level = int(pet.get("pet_level") or 1)
        current_total = int(pet.get("pet_xp") or 0)
        current_row = curve[max(0, min(len(curve) - 1, level - 1))] if curve else {"total_xp": 0, "xp_to_next": 0}
        next_total = int(current_row.get("total_xp") or 0) + int(current_row.get("xp_to_next") or 0)
        remaining = max(0, next_total - current_total) if level < self.get_max_level() else 0
        await session.send_line(f"{pet.get('pet_name')} the {species.get('race_name', 'companion')}")
        await session.send_line(f"  Level {level}   XP {current_total}" + (f"   Next level in {remaining}" if remaining else "   Max level"))
        for ability_key, ability in (species.get("abilities") or {}).items():
            scaling = self._ability_scaling_for_level(species.get("species_key"), ability_key, level)
            state = (pet.get("abilities") or {}).get(ability_key) or {}
            cooldown = max(0, int(state.get("cooldown_until") or 0) - self._now())
            charges = state.get("charges_current")
            detail = []
            if "charges" in scaling:
                detail.append(f"charges {charges if charges is not None else scaling.get('charges', 0)}/{scaling.get('charges', 0)}")
            if cooldown:
                detail.append(f"cooldown {cooldown}s")
            elif int(state.get("cooldown_until") or 0) > 0 or ability_key == "comforting_glow":
                detail.append("ready")
            await session.send_line(f"  {ability.get('label', ability_key)}: {', '.join(detail) if detail else ability.get('description', '')}")

    async def cmd_shop(self, session):
        if not getattr(session, "current_room", None) or not self.is_pet_shop_room(session.current_room.id):
            await session.send_line("You need to be inside Moonwhisker Menagerie to access the companion catalogue.")
            return
        if not getattr(self.server, "pet_web", None):
            await session.send_line("The companion catalogue is unavailable right now.")
            return
        token = self.server.pet_web.generate_token(session)
        url = f"http://{session.server_ip}:{self.server.pet_web.port}{self.system_cfg().get('shop_web_path', '/pets')}?token={token}"
        await session.send_line(colorize(
            "  Moonwhisker Menagerie opens in your browser.",
            TextPresets.EXPERIENCE,
        ))
        await session.send_line(colorize(f"  {url}", TextPresets.SYSTEM))

    async def call_active_pet(self, session):
        pet = getattr(session, "active_pet", None)
        if not pet:
            await session.send_line("You do not have an active companion to call.")
            return
        pet.setdefault("extra_state", {})["dismissed"] = False
        pet["is_released"] = False
        self._save_pet(pet)
        await session.send_line(f"You call for {pet.get('pet_name')}, and it hurries back to your side.")

    async def dismiss_active_pet(self, session):
        pet = getattr(session, "active_pet", None)
        if not pet:
            await session.send_line("You do not have an active companion to dismiss.")
            return
        pet.setdefault("extra_state", {})["dismissed"] = True
        self._save_pet(pet)
        await session.send_line(f"{pet.get('pet_name')} drifts out of sight for now.")

    async def release_active_pet(self, session):
        pet = getattr(session, "active_pet", None)
        if not pet:
            await session.send_line("You do not have an active companion to release.")
            return
        pet["is_active"] = False
        pet["is_released"] = True
        pet.setdefault("extra_state", {})["dismissed"] = True
        self._save_pet(pet)
        progress = getattr(session, "pet_progress", {}) or {}
        progress["active_pet_id"] = None
        session.pet_progress = progress
        self._save_progress(session)
        session.active_pet = None
        if self.server.db and session.character_id:
            self.server.db.set_active_pet(session.character_id, None)
        await session.send_line(f"You send {pet.get('pet_name')} back to Moonwhisker Menagerie.")

    async def feed_active_pet(self, session, item_query: str):
        pet = getattr(session, "active_pet", None)
        if not pet:
            await session.send_line("You do not have an active companion to feed.")
            return
        if pet.get("is_released"):
            await session.send_line("That companion has been sent back to the menagerie.")
            return
        if not item_query:
            await session.send_line("Feed it what?")
            return

        now = self._now()
        cooldown = int(self.system_cfg().get("feed_cooldown_seconds") or 7200)
        last_fed = int(pet.get("last_fed_at") or 0)
        remaining = max(0, cooldown - (now - last_fed)) if last_fed else 0
        if remaining > 0:
            await session.send_line(f"{pet.get('pet_name')} is not ready for another training treat yet.  Try again in {remaining}s.")
            return

        treat = self._find_treat_config(item_query)
        if not treat:
            await session.send_line("That is not a recognized pet training item.")
            return

        inv_item = self._find_inventory_item(session, treat.get("item_short_name"))
        if not inv_item:
            await session.send_line(f"You are not carrying any {treat.get('label', 'pet treat')}.")
            return

        self._consume_inventory_item(session, inv_item)
        gained_levels = self._grant_pet_xp(pet, int(treat.get("xp") or 0))
        pet["last_fed_at"] = now
        pet.setdefault("extra_state", {})["last_treat_key"] = treat.get("key")
        self._save_pet(pet)
        await session.send_line(
            colorize(
                f"You feed {pet.get('pet_name')} a {treat.get('label')}.",
                TextPresets.EXPERIENCE,
            )
        )
        if gained_levels:
            await session.send_line(
                colorize(
                    f"{pet.get('pet_name')} brightens with obvious delight and reaches level {pet.get('pet_level')}!",
                    TextPresets.LEVEL_UP,
                )
            )
        else:
            await session.send_line(
                colorize(
                    f"{pet.get('pet_name')} chirps happily and seems a little more experienced.",
                    TextPresets.SYSTEM,
                )
            )

    async def interact_with_visible_companion(self, session, verb: str, target: str) -> bool:
        room = getattr(session, "current_room", None)
        if not room:
            return False
        entity = self.find_visible_entity(room.id, target, viewer=session)
        if not entity:
            return False

        owner = entity.get("owner")
        subject = entity.get("name")
        if verb == "pet":
            await session.send_line(f"You pet {subject}.")
            await self.server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} pets {subject}.",
                exclude=session,
            )
            if owner and owner is not session:
                await owner.send_line(f"{session.character_name} pets {subject}.")
            return True

        if verb == "touch":
            await session.send_line(f"You reach out and touch {subject}.")
            await self.server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} reaches out and touches {subject}.",
                exclude=session,
            )
            return True

        if verb == "kick":
            await session.send_line(f"You kick toward {subject}, but your foot passes through an invisible ward and the companion remains unharmed.")
            await self.server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} tries to kick {subject}, but an unseen ward turns the motion aside.",
                exclude=session,
            )
            return True
        return False

    # ------------------------------------------------------------------
    # Website data / actions
    # ------------------------------------------------------------------

    def portal_payload(self, session) -> dict:
        progress = getattr(session, "pet_progress", {}) or {}
        species_out = []
        for species_key, species in (self.cfg.get("species") or {}).items():
            price = int(species.get("base_price") or 0)
            if species_key == "floofer" and not progress.get("first_pet_claimed"):
                price = 0
            sale_abilities = [
                self._build_portal_ability(session, None, species_key, ability_key, 1)
                for ability_key in (species.get("abilities") or {}).keys()
            ]
            species_out.append({
                "species_key": species_key,
                "label": species.get("sale_label") or species.get("race_name") or species_key,
                "race_name": species.get("race_name") or species_key.title(),
                "description": species.get("description") or "",
                "price": price,
                "image_path": species.get("image_path") or "",
                "first_pet_only": bool(species.get("free_first_pet")),
                "abilities": sale_abilities,
            })

        pets_out = []
        curve = self.get_xp_curve()
        for pet in getattr(session, "pets", []) or []:
            level = int(pet.get("pet_level") or 1)
            current_row = curve[max(0, min(len(curve) - 1, level - 1))] if curve else {"total_xp": 0, "xp_to_next": 0}
            current_total = int(pet.get("pet_xp") or 0)
            current_floor = int(current_row.get("total_xp") or 0)
            xp_to_next = int(current_row.get("xp_to_next") or 0)
            xp_into_level = max(0, current_total - current_floor)
            pet_abilities = [
                self._build_portal_ability(session, pet, pet.get("species_key"), ability_key, level)
                for ability_key in ((self.species_cfg(pet.get("species_key")) or {}).get("abilities") or {}).keys()
            ]
            pets_out.append({
                "id": pet.get("id"),
                "species_key": pet.get("species_key"),
                "pet_name": pet.get("pet_name"),
                "level": level,
                "xp": current_total,
                "xp_into_level": xp_into_level,
                "xp_to_next": xp_to_next,
                "xp_level_floor": current_floor,
                "active": bool(pet.get("is_active")),
                "released": bool(pet.get("is_released")),
                "image_path": (self.species_cfg(pet.get("species_key")) or {}).get("image_path") or "",
                "equipment": list((pet.get("equipment") or {}).keys()),
                "abilities": pet_abilities,
            })

        return {
            "character": {
                "name": getattr(session, "character_name", "unknown"),
                "silver": int(getattr(session, "silver", 0) or 0),
                "progress": progress,
            },
            "shop": {
                "name": self.system_cfg().get("shop_name") or "Moonwhisker Menagerie",
                "entry_display": self.shop_entry_display(),
                "shopkeeper": self.cfg.get("shopkeeper") or {},
            },
            "species_for_sale": species_out,
            "treats": self.cfg.get("treats") or [],
            "pet_slots": self.cfg.get("pet_slots") or [],
            "pets": pets_out,
        }

    def buy_pet(self, session, species_key: str, pet_name: str = "") -> tuple[bool, str, Optional[dict]]:
        if not getattr(session, "current_room", None) or not self.is_pet_shop_room(session.current_room.id):
            return False, "You must be inside Moonwhisker Menagerie to purchase a pet.", None

        progress = getattr(session, "pet_progress", {}) or {}
        if progress.get("quest_state") not in {"accepted", "completed"}:
            return False, "You must ACCEPT Twillip's pet tutorial before claiming a companion.", None

        species = self.species_cfg(species_key)
        if not species:
            return False, "Unknown pet species.", None

        pet_name = (pet_name or "").strip()
        if pet_name:
            ok, err = self.validate_pet_name(session, pet_name)
            if not ok:
                return False, err, None
        else:
            pet_name = self._default_pet_name(species)

        if not progress.get("first_pet_claimed") and species_key != "floofer":
            return False, "You must claim your free Floofer before other companions become available.", None

        price = int(species.get("base_price") or 0)
        if species_key == "floofer" and not progress.get("first_pet_claimed"):
            price = 0
        if int(getattr(session, "silver", 0) or 0) < price:
            return False, "You do not have enough silver for that companion.", None

        pet_id = self.server.db.create_character_pet(
            session.character_id,
            species_key,
            pet_name,
            image_key=species.get("image_key"),
            active=True,
            extra_state={"dismissed": False},
        )
        if not pet_id:
            return False, "The menagerie could not complete that purchase.", None

        if price > 0:
            session.silver = max(0, int(session.silver or 0) - price)
            self.server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver,
            )

        pet = {
            "id": int(pet_id),
            "character_id": int(session.character_id),
            "species_key": species_key,
            "pet_name": pet_name,
            "pet_level": 1,
            "pet_xp": 0,
            "is_active": True,
            "is_deleted": False,
            "is_released": False,
            "image_key": species.get("image_key"),
            "last_fed_at": 0,
            "last_random_emote_at": 0,
            "last_state_emote_at": 0,
            "extra_state": {"dismissed": False},
            "abilities": {},
            "equipment": {},
        }
        session.pets = [p for p in (session.pets or []) if p.get("id") != pet["id"]]
        session.pets.append(pet)
        self.server.db.set_active_pet(session.character_id, pet["id"])
        progress["active_pet_id"] = pet["id"]
        session.pet_progress = progress
        self._save_progress(session)
        self._seed_pet_abilities(pet)
        self._refresh_pet_reference(session)

        if not progress.get("first_pet_claimed"):
            progress["first_pet_claimed"] = True
            session.pet_progress = progress
            self._save_progress(session)

        return True, "Pet purchased successfully. Choose a name for your new companion.", pet

    def rename_pet_from_shop(self, session, pet_id: int, pet_name: str) -> tuple[bool, str]:
        if not getattr(session, "current_room", None) or not self.is_pet_shop_room(session.current_room.id):
            return False, "You may only rename companions inside Moonwhisker Menagerie."
        target = next((p for p in (session.pets or []) if int(p.get("id") or 0) == int(pet_id or 0) and not p.get("is_deleted")), None)
        if not target:
            return False, "That companion is not available."
        pet_name = (pet_name or "").strip()
        ok, err = self.validate_pet_name(session, pet_name, exclude_pet_id=target.get("id"))
        if not ok:
            return False, err
        target["pet_name"] = pet_name
        self._save_pet(target)
        self._refresh_pet_reference(session)
        return True, f"{pet_name} is now bonded to you."

    def buy_pet_item(self, session, treat_key: str, quantity: int = 1) -> tuple[bool, str]:
        if not getattr(session, "current_room", None) or not self.is_pet_shop_room(session.current_room.id):
            return False, "You must be inside Moonwhisker Menagerie to purchase pet items."
        treat = None
        for row in self.cfg.get("treats") or []:
            if row.get("key") == treat_key:
                treat = row
                break
        if not treat:
            return False, "Unknown pet item."
        quantity = max(1, min(int(quantity or 1), 99))
        total_cost = int(treat.get("price") or 0) * quantity
        if int(getattr(session, "silver", 0) or 0) < total_cost:
            return False, "You do not have enough silver for that purchase."
        template = self.server.db.get_item_template_by_short_name(treat.get("item_short_name"))
        if not template:
            return False, "The requested pet item template does not exist."
        inv_id = self.server.db.add_item_to_inventory(session.character_id, int(template["id"]), quantity=quantity)
        if not inv_id:
            return False, "The menagerie could not hand over that item."
        session.silver = max(0, int(session.silver or 0) - total_cost)
        self.server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver,
        )
        from server.core.commands.player.inventory import restore_inventory_state
        restore_inventory_state(self.server, session)
        return True, f"Purchased {quantity}x {treat.get('label')}."

    def set_active_pet_from_shop(self, session, pet_id: int) -> tuple[bool, str]:
        if not getattr(session, "current_room", None) or not self.is_pet_shop_room(session.current_room.id):
            return False, "You may only swap companions inside Moonwhisker Menagerie."
        target = next((p for p in (session.pets or []) if int(p.get("id") or 0) == int(pet_id or 0) and not p.get("is_deleted")), None)
        if not target:
            return False, "That companion is not available."
        for pet in session.pets:
            pet["is_active"] = False
        target["is_active"] = True
        target["is_released"] = False
        target.setdefault("extra_state", {})["dismissed"] = False
        self.server.db.set_active_pet(session.character_id, target["id"])
        self._save_pet(target)
        session.pet_progress["active_pet_id"] = target["id"]
        self._save_progress(session)
        self._refresh_pet_reference(session)
        return True, f"{target.get('pet_name')} is now your active companion."

    def delete_pet_from_shop(self, session, pet_id: int) -> tuple[bool, str]:
        if not getattr(session, "current_room", None) or not self.is_pet_shop_room(session.current_room.id):
            return False, "You may only remove companions from within Moonwhisker Menagerie."
        target = next((p for p in (session.pets or []) if int(p.get("id") or 0) == int(pet_id or 0) and not p.get("is_deleted")), None)
        if not target:
            return False, "That companion is not available."
        if not self.server.db.soft_delete_character_pet(session.character_id, target["id"]):
            return False, "The menagerie could not complete that removal."
        session.pets = [p for p in session.pets if p.get("id") != target["id"]]
        if session.active_pet and session.active_pet.get("id") == target["id"]:
            session.active_pet = None
            session.pet_progress["active_pet_id"] = None
            self._save_progress(session)
        return True, f"{target.get('pet_name')} has been permanently released from your care."

    def validate_pet_name(self, session, pet_name: str, exclude_pet_id: int | None = None) -> tuple[bool, str]:
        naming = self.system_cfg().get("naming") or {}
        min_len = int(naming.get("min_length") or 3)
        max_len = int(naming.get("max_length") or 18)
        pattern = naming.get("allow_pattern") or r"^[A-Za-z][A-Za-z' %-]+$"
        if len(pet_name) < min_len or len(pet_name) > max_len:
            return False, f"Pet names must be between {min_len} and {max_len} characters."
        if not re.match(pattern, pet_name):
            return False, "Pet names may contain letters, spaces, apostrophes, and hyphens only."
        existing = {
            str(p.get("pet_name") or "").lower()
            for p in (getattr(session, "pets", []) or [])
            if int(p.get("id") or 0) != int(exclude_pet_id or 0)
        }
        if pet_name.lower() in existing:
            return False, "You already own a pet with that name."
        return True, ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _send_lines(self, session, lines: List[str]):
        for line in lines:
            await session.send_line(colorize(f"  {line}", TextPresets.NPC_SPEECH if '"' in line else TextPresets.NPC_EMOTE))

    def _seed_pet_abilities(self, pet: dict):
        species = self.species_cfg(pet.get("species_key"))
        for ability_key in (species.get("abilities") or {}).keys():
            state = self._ensure_ability_state(pet, ability_key)
            scaling = self._ability_scaling_for_level(pet.get("species_key"), ability_key, pet.get("pet_level"))
            if "charges" in scaling:
                state["charges_current"] = int(scaling.get("charges") or 0)
            state["cooldown_until"] = 0
            state["last_triggered_at"] = 0
            self._save_pet_ability(pet, ability_key)

    def _default_pet_name(self, species: dict) -> str:
        race_name = str(species.get("race_name") or "Companion").strip()
        return f"Unnamed {race_name}"

    def _find_treat_config(self, query: str) -> Optional[dict]:
        query = (query or "").strip().lower()
        for row in self.cfg.get("treats") or []:
            names = {
                (row.get("key") or "").lower(),
                (row.get("short_name") or "").lower(),
                (row.get("item_short_name") or "").lower(),
                (row.get("label") or "").lower(),
            }
            if any(query == name or query in name for name in names if name):
                return row
        return None

    def _find_inventory_item(self, session, short_name: str) -> Optional[dict]:
        wanted = (short_name or "").strip().lower()
        for item in getattr(session, "inventory", []) or []:
            if (item.get("short_name") or "").lower() == wanted:
                return item
        return None

    def _consume_inventory_item(self, session, item: dict):
        inv_id = item.get("inv_id")
        qty = int(item.get("quantity") or 1)
        if qty > 1:
            self.server.db.execute_update(
                "UPDATE character_inventory SET quantity = quantity - 1 WHERE id = %s",
                (int(inv_id),),
            )
        else:
            self.server.db.remove_item_from_inventory(int(inv_id))
        from server.core.commands.player.inventory import restore_inventory_state
        restore_inventory_state(self.server, session)

    def _grant_pet_xp(self, pet: dict, xp_amount: int) -> int:
        curve = self.get_xp_curve()
        if not curve:
            return 0
        max_level = self.get_max_level()
        before = int(pet.get("pet_level") or 1)
        pet["pet_xp"] = int(pet.get("pet_xp") or 0) + max(0, int(xp_amount or 0))
        new_level = before
        for row in curve:
            if int(row.get("level") or 0) <= max_level and pet["pet_xp"] >= int(row.get("total_xp") or 0):
                new_level = max(new_level, int(row.get("level") or new_level))
        pet["pet_level"] = min(max_level, new_level)
        leveled = max(0, int(pet["pet_level"]) - before)
        if leveled:
            for ability_key in (self.species_cfg(pet.get("species_key")).get("abilities") or {}).keys():
                state = self._ensure_ability_state(pet, ability_key)
                scaling = self._ability_scaling_for_level(pet.get("species_key"), ability_key, pet.get("pet_level"))
                if "charges" in scaling:
                    state["charges_current"] = max(int(state.get("charges_current") or 0), int(scaling.get("charges") or 0))
                    self._save_pet_ability(pet, ability_key)
        return leveled
