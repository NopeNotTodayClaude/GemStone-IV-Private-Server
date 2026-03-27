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
        self.profession_id = 0
        self.gender = "female"
        self.age = 0  # Set from DB or defaulted by race on load

        # Stats (base values)
        self.level = 1
        self.experience = 0
        self.field_experience = 0

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

        # Training
        self.physical_tp = 0
        self.mental_tp = 0
        self.skills = {}  # skill_id -> {ranks, bonus}

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
        self.stance = "neutral"

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

        # Inventory (loaded from DB)
        self.inventory = []  # list of dicts from DB

        # Hand tracking (GS4 style left/right hand)
        self.right_hand = None  # item dict or None
        self.left_hand = None   # item dict or None

        # Character creation temp state
        self._creation_data = {}

    def load_from_db(self, char_data):
        """Populate session from a database character record."""
        self.character_id = char_data["id"]
        self.character_name = char_data["name"]
        self.race_id = char_data["race_id"]
        self.profession_id = char_data["profession_id"]
        self.gender = char_data.get("gender", "female")

        # Age: use stored value or default by race (GS4 canon starting ages)
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

        def _int(key, default=0):
            return int(char_data.get(key) or default)

        self.level           = _int("level", 1)
        self.experience      = _int("experience", 0)
        self.field_experience = _int("field_experience", 0)

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

        self.height = char_data.get("height", 70)
        self.hair_color = char_data.get("hair_color", "brown")
        self.hair_style = char_data.get("hair_style", "short")
        self.eye_color = char_data.get("eye_color", "blue")

        self.position = char_data.get("position", "standing")
        self.stance = (char_data.get("stance") or "neutral").lower()
        self.skills = char_data.get("skills", {})

        self.tutorial_complete = bool(char_data.get("tutorial_complete", 0))
        self.tutorial_stage = char_data.get("tutorial_stage", 0)

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
        """
        Send the command prompt, preceded by a GSIV status tag that the HUD
        parses for HP / MP / Spirit / Stamina / RT / Room updates.

        Tag format (all on one line, filtered out by the HUD client):
            <GSIV HP=85/100 MP=40/100 SP=10/10 ST=100/100 RT=0 ROOM=1234>
        """
        rt = self.get_roundtime()
        room_id = self.current_room.id if self.current_room else 0

        # ── HUD status tag ─────────────────────────────────────────────────
        # The client hides this line; raw telnet users will just see it pass.
        status_tag = (
            f"<GSIV "
            f"HP={self.health_current}/{self.health_max} "
            f"MP={self.mana_current}/{self.mana_max} "
            f"SP={self.spirit_current}/{self.spirit_max} "
            f"ST={self.stamina_current}/{self.stamina_max} "
            f"RT={rt} "
            f"ROOM={room_id}>"
        )
        await self.send_line(status_tag)
        # ───────────────────────────────────────────────────────────────────

        if rt > 0:
            await self.send(f"[RT: {rt}s]>")
        else:
            await self.send(">")

    def get_roundtime(self):
        remaining = self.roundtime_end - time.time()
        return max(0, int(remaining))

    def set_roundtime(self, seconds):
        self.roundtime_end = time.time() + seconds

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
            if session.character_id and hasattr(self.server, 'db') and self.server.db:
                self.server.db.save_character(session)
                log.info("Character saved on disconnect: %s", session.character_name)

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
