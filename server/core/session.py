"""
Session management - tracks connected players and their state.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, List

log = logging.getLogger(__name__)


class Session:
    """Represents a single connected player session."""

    _next_id = 1

    def __init__(self, reader, writer, addr, server):
        self.id = Session._next_id
        Session._next_id += 1

        self._reader = reader
        self._writer = writer
        self.addr = addr
        self.server = server

        self.connected = True
        self.connect_time = time.time()
        self.last_input_time = time.time()
        self.last_save_time = time.time()

        # Authentication state
        self.state = "login"  # login, account_login, account_create, character_select,
                              # character_create, race_select, profession_select,
                              # stat_assign, appearance, playing, tutorial
        self.account_id = None
        self.account_data = None

        # Character data (populated after login/create)
        self.character_name = None
        self.character_id = None
        self.race = None
        self.race_id = 0
        self.profession = None
        self.profession_name = None
        self.profession_id = 0
        self.gender = "female"
        self.age = 0  # Set from DB or defaulted by race on load

        # Stats (base values)
        self.level = 1
        self.experience = 0
        self.field_experience = 0
        self.fame = 0
        self.fame_list_opt_in = False

        self.stat_strength = 50
        self.stat_constitution = 50
        self.stat_dexterity = 50
        self.stat_agility = 50
        self.stat_discipline = 50
        self.stat_aura = 50
        self.stat_logic = 50
        self.stat_intuition = 50
        self.stat_wisdom = 50
        self.stat_influence = 50

        # Stat baseline snapshot (set at creation, never changes)
        self.base_stat_strength     = 50
        self.base_stat_constitution = 50
        self.base_stat_dexterity    = 50
        self.base_stat_agility      = 50
        self.base_stat_discipline   = 50
        self.base_stat_aura         = 50
        self.base_stat_logic        = 50
        self.base_stat_intuition    = 50
        self.base_stat_wisdom       = 50
        self.base_stat_influence    = 50

        # Stat reallocation tracking
        self.fixstat_uses_remaining = 10   # 10 free uses before level 20
        self.fixstat_uses_total     = 0    # lifetime total uses
        self.fixstat_last_free      = None # timestamp of last post-20 free use

        # Conversion loan tracking (for lossless CONVERT REFUND)
        self.ptp_loaned = 0   # PTP currently borrowed from MTP pool
        self.mtp_loaned = 0   # MTP currently borrowed from PTP pool

        # Resource pools
        self.health_current = 100
        self.health_max = 100
        self.mana_current = 0
        self.mana_max = 0
        self.spirit_current = 10
        self.spirit_max = 10
        self.stamina_current = 100
        self.stamina_max = 100

        # Economy
        self.silver = 0
        self.bank_silver = 0
        self.locker_open_location_id = None
        self.locker_open_town_name = None

        # Training
        self.physical_tp = 0
        self.mental_tp = 0
        self.skills = {}  # skill_id -> {ranks, bonus}
        self.guild_membership = None
        self.guild_skills = {}
        self.guild_tasks = []

        # Appearance
        self.height = 70
        self.hair_color = "brown"
        self.hair_style = "short"
        self.eye_color = "blue"

        # World state
        self.current_room = None
        self.previous_room = None

        # Combat state
        self.in_combat = False
        self.target = None
        self.roundtime_end = 0
        self.stance = "offensive"
        # Persistent AIM preference — None means random, otherwise a location string
        # e.g. "head", "right arm", "neck". Saved to DB and survives login.
        self.aimed_location: str | None = None

        # Gift of Lumnis state — per-character, persisted to DB
        # 0=inactive, 1=phase1 (3x absorption), 2=phase2 (2x absorption)
        self.lumnis_phase:        int   = 0
        self.lumnis_bonus_earned: int   = 0    # total bonus XP absorbed this cycle
        self.lumnis_cycle_id            = None  # DB cycle start timestamp

        # Spell state
        self.prepared_spell = None
        self.active_spells = {}

        # Status
        self.position = "standing"
        self.hidden = False
        self.sneaking = False
        self.invisible = False

        # Death state
        self.is_dead              = False   # True while dead/waiting for Beefy
        self.death_choice_pending = False   # True while death menu is shown
        self.death_room_id        = None    # Room where player died
        self.death_stat_mult      = 1.0     # 1.0 = normal; 0.1 = 90% penalty after ghost revival

        # Injuries: {location: severity 1-5}  — persist until healed
        self.injuries = {}

        # Active status effects: {effect_name: {duration, stacks, ...}}
        self.status_effects = {}

        # Tutorial tracking
        self.tutorial_stage = 0
        self.tutorial_complete = False

        # Pet / companion system
        self.pet_progress = {}
        self.pets = []
        self.active_pet = None
        self.pet_sprite_visible = False
        self.pet_room_moves = 0
        self.pet_last_shop_room_id = None

        # Inventory (loaded from DB)
        self.inventory = []  # list of dicts from DB

        # Hand tracking (GS4 style left/right hand)
        self.right_hand = None  # item dict or None
        self.left_hand = None   # item dict or None
        self.ready_ammo_inv_id = None
        self.ready_ammo_type = None
        self.ready_ammo_name = None

        # Character creation temp state
        self._creation_data = {}

    def load_from_db(self, char_data):
        """Populate session from a database character record."""
        self.character_id = char_data["id"]
        self.character_name = char_data["name"]
        self.race_id = char_data["race_id"]
        self.profession_id = char_data["profession_id"]
        self.profession = char_data.get("profession_name", "") or None
        self.profession_name = char_data.get("profession_name", "") or None
        self.gender = char_data.get("gender", "female")

        # Age: use stored value or default by race (GS4 canon starting ages)
        # Elves/Sylvans: 50+, Humans: 20+, Dwarves: 50+, Halflings: 30+,
        # Giantmen: 20+, Gnomes: 30+, Half-Elves: 20+, Aelotoi: 20+, Erithian: 20+
        RACE_DEFAULT_AGES = {
            1: 20,   # Human
            2: 50,   # Elf
            3: 50,   # Dark Elf
            4: 20,   # Half-Elf
            5: 50,   # Dwarf
            6: 30,   # Halfling
            7: 20,   # Giantman
            8: 30,   # Forest Gnome
            9: 30,   # Burghal Gnome
            10: 50,  # Sylvankind
            11: 20,  # Aelotoi
            12: 20,  # Erithian
            13: 20,  # Half-Krolvin
        }
        stored_age = int(char_data.get("age") or 0)
        if stored_age > 0:
            self.age = stored_age
        else:
            self.age = RACE_DEFAULT_AGES.get(char_data.get("race_id", 1), 20)
        # Cast everything to plain int -- MySQL DECIMAL/BIGINT columns come back
        # as decimal.Decimal objects which break float arithmetic downstream.
        def _int(key, default=0):
            return int(char_data.get(key) or default)

        self.level           = _int("level", 1)
        self.experience      = _int("experience", 0)
        self.field_experience = _int("field_experience", 0)
        self.fame            = _int("fame", 0)
        self.fame_list_opt_in = bool(_int("fame_list_opt_in", 0))

        self.stat_strength     = _int("stat_strength", 50)
        self.stat_constitution = _int("stat_constitution", 50)
        self.stat_dexterity    = _int("stat_dexterity", 50)
        self.stat_agility      = _int("stat_agility", 50)
        self.stat_discipline   = _int("stat_discipline", 50)
        self.stat_aura         = _int("stat_aura", 50)
        self.stat_logic        = _int("stat_logic", 50)
        self.stat_intuition    = _int("stat_intuition", 50)
        self.stat_wisdom       = _int("stat_wisdom", 50)
        self.stat_influence    = _int("stat_influence", 50)

        self.health_current  = _int("health_current", 100)
        self.health_max      = _int("health_max", 100)
        self.mana_current    = _int("mana_current", 0)
        self.mana_max        = _int("mana_max", 0)
        self.spirit_current  = _int("spirit_current", 10)
        self.spirit_max      = _int("spirit_max", 10)
        self.stamina_current = _int("stamina_current", 100)
        self.stamina_max     = _int("stamina_max", 100)

        self.silver      = _int("silver", 0)
        self.bank_silver = _int("bank_silver", 0)
        self.physical_tp = _int("physical_tp", 0)
        self.mental_tp   = _int("mental_tp", 0)

        # Base stat snapshot
        self.base_stat_strength     = _int("base_stat_strength",     self.stat_strength)
        self.base_stat_constitution = _int("base_stat_constitution", self.stat_constitution)
        self.base_stat_dexterity    = _int("base_stat_dexterity",    self.stat_dexterity)
        self.base_stat_agility      = _int("base_stat_agility",      self.stat_agility)
        self.base_stat_discipline   = _int("base_stat_discipline",   self.stat_discipline)
        self.base_stat_aura         = _int("base_stat_aura",         self.stat_aura)
        self.base_stat_logic        = _int("base_stat_logic",        self.stat_logic)
        self.base_stat_intuition    = _int("base_stat_intuition",    self.stat_intuition)
        self.base_stat_wisdom       = _int("base_stat_wisdom",       self.stat_wisdom)
        self.base_stat_influence    = _int("base_stat_influence",    self.stat_influence)

        # Fixstat tracking
        self.fixstat_uses_remaining = _int("fixstat_uses_remaining", 10)
        self.fixstat_uses_total     = _int("fixstat_uses_total",     0)
        raw_last_free = char_data.get("fixstat_last_free", None)
        self.fixstat_last_free = (
            raw_last_free.timestamp()
            if raw_last_free and hasattr(raw_last_free, "timestamp")
            else (float(raw_last_free) if raw_last_free else None)
        )

        # Conversion loan tracking
        self.ptp_loaned = _int("ptp_loaned", 0)
        self.mtp_loaned = _int("mtp_loaned", 0)

        self.height = char_data.get("height", 70)
        self.hair_color = char_data.get("hair_color", "brown")
        self.hair_style = char_data.get("hair_style", "short")
        self.eye_color = char_data.get("eye_color", "blue")

        self.position = char_data.get("position", "standing")
        self.stance = (char_data.get("stance") or "neutral").lower()
        self.skills = char_data.get("skills", {})
        self.guild_membership = char_data.get("guild_membership")
        self.guild_skills = char_data.get("guild_skills", {})
        self.guild_tasks = char_data.get("guild_tasks", [])
        self.starting_room_id = _int("starting_room_id", _int("current_room_id", 221))

        # Load tutorial state from database (0/1 -> bool for tutorial_complete)
        self.tutorial_complete = bool(char_data.get("tutorial_complete", 0))
        self.tutorial_stage = char_data.get("tutorial_stage", 0)

        # Load persistent AIM preference
        raw_aim = char_data.get("aimed_location", None)
        self.aimed_location = raw_aim if raw_aim else None

        # Load Lumnis state
        self.lumnis_phase        = int(char_data.get("lumnis_phase",        0) or 0)
        self.lumnis_bonus_earned = int(char_data.get("lumnis_bonus_earned", 0) or 0)
        self.lumnis_cycle_id     = char_data.get("lumnis_cycle_id", None)

    async def send(self, text):
        """Send text to the client."""
        if not self.connected:
            return
        try:
            self._writer.write(text.encode("utf-8"))
            await self._writer.drain()
        except (ConnectionResetError, BrokenPipeError, OSError):
            self.connected = False

    async def send_line(self, text=""):
        """Send text followed by newline."""
        await self.send(text + "\r\n")

    async def send_prompt(self):
        """Send the command prompt."""
        rt = self.get_roundtime()
        if rt > 0:
            await self.send(f"[RT: {rt}s]>")
        else:
            await self.send(">")

    def get_roundtime(self):
        remaining = self.roundtime_end - time.time()
        return max(0, int(remaining))

    def set_roundtime(self, seconds):
        self.roundtime_end = time.time() + float(seconds)

    def disconnect(self):
        self.connected = False

    def __repr__(self):
        name = self.character_name or "unknown"
        return f"Session({self.id}, {name}, {self.addr[0]}:{self.addr[1]})"


class SessionManager:
    """Manages all active player sessions."""

    def __init__(self, server):
        self.server = server
        self._sessions: Dict[int, Session] = {}

    def create_session(self, reader, writer, addr) -> Session:
        session = Session(reader, writer, addr, self.server)
        self._sessions[session.id] = session
        log.info("Session created: %s", session)
        return session

    def remove_session(self, session: Session):
        if session.id in self._sessions:
            assault_state = getattr(session, "weapon_assault_state", None) or {}
            assault_task = assault_state.get("task")
            if assault_task and not assault_task.done():
                assault_task.cancel()
            session.weapon_assault_state = None

            # Save character before removing
            if session.character_id:
                try:
                    wound_bridge = getattr(self.server, 'wound_bridge', None)
                    if wound_bridge:
                        wound_bridge.save_wounds_now(session)
                except Exception as _e:
                    log.debug("Wound save on disconnect failed: %s", _e)
            if session.character_id and hasattr(self.server, 'db') and self.server.db:
                self.server.db.save_character(session)
                log.info("Character saved on disconnect: %s", session.character_name)

            # Revoke sync token and close sync connection
            if session.character_id:
                try:
                    sync_srv = getattr(self.server, 'sync_server', None)
                    if sync_srv:
                        sync_srv.disconnect(session.character_id)
                        sync_srv.evict_token(session.character_id)
                    if hasattr(self.server, 'db') and self.server.db:
                        from server.core.sync.sync_auth import revoke_token
                        revoke_token(self.server.db, session.character_id)
                except Exception as _e:
                    log.debug("Sync cleanup error on disconnect: %s", _e)

            if session.current_room:
                self.server.world.remove_player_from_room(
                    session, session.current_room.id
                )
            del self._sessions[session.id]
            log.info("Session removed: %s", session)

    def get_session(self, session_id: int) -> Optional[Session]:
        return self._sessions.get(session_id)

    def find_by_name(self, name: str) -> Optional[Session]:
        name_lower = name.lower()
        for s in self._sessions.values():
            if s.character_name and s.character_name.lower() == name_lower:
                return s
        return None

    def all(self) -> List[Session]:
        return list(self._sessions.values())

    def playing(self) -> List[Session]:
        return [s for s in self._sessions.values() if s.state == "playing"]

    @property
    def count(self):
        return len(self._sessions)

    @property
    def playing_count(self):
        return len(self.playing())
