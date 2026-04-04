"""
GameServer - Main server class.
Full account system, character creation, DB persistence, auto-save.
"""

import asyncio
import logging
import time
import os
import sys

from server.core.session import SessionManager, Session
from server.core.world.world_manager import WorldManager
from server.core.commands.command_router import CommandRouter
from server.core.engine.game_loop import GameLoop
from server.core.database import Database
from server.core.character_creation import CharacterCreator
from server.core.tutorial import TutorialManager
from server.core.tutorial import is_tutorial_room_id
from server.core.character_unlocks import load_unlocks_for_session
from server.core.entity.creature.creature_manager import CreatureManager
from server.core.entity.npc.npc_manager import NPCManager
from server.core.engine.combat.combat_engine import CombatEngine
from server.core.engine.experience.experience_manager import ExperienceManager
from server.core.engine.events.event_manager import EventManager
from server.core.engine.weather.weather_manager import WeatherManager
from server.core.engine.combat.status_effects import StatusEffectManager
from server.core.engine.status_manager import StatusManager
from server.core.engine.death.death_manager import DeathManager
from server.core.web.training_server import TrainingWebServer
from server.core.web.character_creator_server import CharacterCreatorWebServer
from server.core.web.pet_server import PetWebServer
from server.core.protocol.colors import colorize, TextPresets
from server.core.scripting.lua_manager import LuaManager
from server.core.scripting.wound_bridge import WoundBridge
from server.core.sync.sync_server import SyncServer
from server.core.sync.sync_broadcaster import SyncBroadcaster
from server.core.commands.player.party import PartyManager
from server.core.engine.guild_engine import GuildEngine
from server.core.engine.tracking.trail_tracker import TrailTracker
from server.core.engine.pets.pet_manager import PetManager
from server.core.engine.traps import TrapManager
from server.core.engine.hotbar_manager import HotbarManager
from server.core.engine.ferry_manager import FerryManager
from server.core.engine.inn_manager import InnManager
from server.core.engine.travel_office_manager import TravelOfficeManager
from server.core.engine.justice_manager import JusticeManager
from server.core.engine.fake_player_manager import FakePlayerManager
from server.core.engine.town_trouble_manager import TownTroubleManager
from server.core.engine.spell_summon_manager import SpellSummonManager
from server.core.services.persistence_writer import PersistenceWriterService
from server.core.commands.player.training import _try_load_lua_skills, apply_mana_max_recalc
from server.core.commands.player.inventory import restore_inventory_state
from server.core.scripting.loaders.ambush_loader import load_ambush_cfg
from server.core.scripting.loaders.perception_loader import load_perception_cfg
from server.core.scripting.loaders.weapon_techniques_loader import sync_weapon_techniques
from server.core.scripting.loaders.combat_maneuvers_loader import sync_combat_maneuvers
from server.core.scripting.lua_bindings.weapon_api import (
    load_techniques_for_session,
    reconcile_techniques_for_session,
)
from server.core.scripting.lua_bindings.combat_maneuver_api import load_combat_maneuvers_for_session

log = logging.getLogger(__name__)

# How often to auto-save each player (seconds)
AUTOSAVE_INTERVAL = 300


class GameServer:
    """Main game server - binds everything together."""

    def __init__(self, config):
        self.config = config
        self.host = config.get("server.host", "0.0.0.0")
        self.port = config.get("server.port", 4901)
        self.running = False

        # Core subsystems
        self.sessions = SessionManager(self)
        self.world = WorldManager(self)
        self.commands = CommandRouter(self)
        self.game_loop = GameLoop(self)
        self.db = Database(config)
        self.persistence_writer = PersistenceWriterService(config)
        self.char_creator = CharacterCreator(self)
        self.tutorial = TutorialManager(self)
        self.lua = LuaManager(self)
        self.wound_bridge    = WoundBridge(self)
        self.sync_server     = SyncServer(self)
        self.sync_broadcaster = SyncBroadcaster(self)

        # New subsystems
        self.creatures = CreatureManager(self)
        self.npcs = NPCManager(self)
        self.combat = CombatEngine(self)
        self.experience = ExperienceManager(self)
        self.events = EventManager(self)
        self.weather = WeatherManager(self)
        self.status_effects = StatusEffectManager(self)   # legacy shim — kept for old combat imports
        self.status         = StatusManager(self)          # NEW: canonical status engine
        self.death = DeathManager(self)
        self.party_manager   = PartyManager()               # Co-op party system
        self.guild = GuildEngine(self)
        self.tracking = TrailTracker(self)
        self.pets = PetManager(self)
        self.traps = TrapManager(self)
        self.hotbar = HotbarManager(self)
        self.ferries = FerryManager(self)
        self.inns = InnManager(self)
        self.travel_offices = TravelOfficeManager(self)
        self.justice = JusticeManager(self)
        self.fake_players = FakePlayerManager(self)
        self.town_trouble = TownTroubleManager(self)
        self.spell_summons = SpellSummonManager(self)
        self.perception_cfg  = {}                           # Loaded from globals/perception.lua after Lua init

        self._tcp_server  = None
        self._loop = None
        self.training_web = None
        self.char_web = None
        self.pet_web = None
        self._loop = None

    def start(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._start_async())
        finally:
            self._loop.close()

    async def _start_async(self):
        log.info("=" * 60)
        log.info("Starting GemStone IV Private Server v0.2.0")
        log.info("=" * 60)

        # Connect to database
        db_ok = self.db.connect()
        if db_ok:
            log.info("Database connected.")
            try:
                self.persistence_writer.start()
            except Exception as _writer_exc:
                log.error("Persistence writer failed to start: %s", _writer_exc, exc_info=True)
        else:
            log.warning("Database unavailable - running without persistence!")

        # Boot Lua engine — must be first, world/NPCs/creatures depend on scripts
        log.info("Initialising Lua scripting engine...")
        await self.lua.initialize()
        if self.lua.engine and self.lua.engine.available:
            log.info("Lua engine ready.")
        else:
            log.warning("Lua engine unavailable — falling back to hardcoded Python data.")

        _try_load_lua_skills(self)
        try:
            defs = self.lua.get_weapon_techniques() or {}
            synced = sync_weapon_techniques(self.db, defs) if self.db and defs else 0
            log.info("Weapon techniques synced from Lua (%d defs)", synced)
        except Exception as _wt_err:
            log.error("Weapon technique sync failed: %s", _wt_err, exc_info=True)
        try:
            defs = self.lua.get_combat_maneuvers() or {}
            synced = sync_combat_maneuvers(self.db, defs) if self.db and defs else 0
            log.info("Combat maneuvers synced from Lua (%d defs)", synced)
        except Exception as _cman_err:
            log.error("Combat maneuver sync failed: %s", _cman_err, exc_info=True)

        # Load perception system config from Lua (scripts/globals/perception.lua)
        # Loaded before wound_bridge so all subsystems can reference it via server.perception_cfg
        _lua_eng = self.lua.engine if (self.lua.engine and self.lua.engine.available) else None
        self.perception_cfg = load_perception_cfg(_lua_eng)
        log.info("Perception system loaded (skill_id=%d, rank_mult=%d)",
                 self.perception_cfg["skill_id"], self.perception_cfg["rank_multiplier"])

        self.ambush_cfg = load_ambush_cfg(_lua_eng)
        log.info("Ambush system loaded (skill_id=%d, cm_skill_id=%d)",
                 self.ambush_cfg.get("skill_id", 43), self.ambush_cfg.get("cm_skill_id", 4))

        # Initialise wound bridge (must be after Lua)
        await self.wound_bridge.initialize()
        log.info("WoundBridge ready (Lua-backed: %s)", self.wound_bridge.available)

        # Load perception system config from Lua
        self.perception_cfg = load_perception_cfg(self.lua.engine)
        log.info("Perception system config loaded (skill_id=%d)", self.perception_cfg.get("skill_id", 27))

        self.ambush_cfg = load_ambush_cfg(self.lua.engine)
        log.info("Ambush system config loaded (skill_id=%d)", self.ambush_cfg.get("skill_id", 43))

        # Seed spells table from Lua circle modules
        log.info("Seeding spell circles...")
        _spell_summary = await self.lua.seed_spells()
        _spell_total   = sum(_spell_summary.values())
        log.info("Spell seeding complete: %d spell(s) across %d circle(s).",
                 _spell_total, len(_spell_summary))

        # Boot material weight cache — reads weight_modifier from Lua materials
        # so encumbrance.py has zero I/O cost per-swing on weight lookups.
        # Must live in material_weight (outside combat package) to avoid circular imports.
        from server.core.engine.material_weight import init_weight_cache as _init_weight_cache
        _init_weight_cache(self)

        # Load world
        log.info("Loading world...")
        await self.world.initialize()
        log.info("World loaded: %d zones, %d rooms",
                 self.world.zone_count, self.world.room_count)

        await self.ferries.initialize()
        log.info("Ferry system ready")

        await self.inns.initialize()
        log.info("Inn system ready")

        await self.travel_offices.initialize()
        log.info("Travel office system ready")

        await self.justice.initialize()
        log.info("Justice system ready")

        # Spawn creatures
        log.info("Spawning creatures...")
        await self.creatures.initialize()
        log.info("Creatures spawned: %d total", self.creatures.creature_count)

        # Spawn NPCs
        log.info("Spawning NPCs...")
        await self.npcs.initialize()
        log.info("NPCs spawned: %d total", len(self.npcs._npcs))

        await self.fake_players.initialize()
        log.info("Fake player system ready")

        await self.town_trouble.initialize()
        log.info("Town trouble system ready")

        # Load experience level table from DB
        log.info("Loading experience level table...")
        await self.experience.initialize()
        log.info("Experience system ready (%d levels loaded)", len(self.experience._level_table))

        # Weather system
        await self.weather.initialize()
        log.info("Weather system ready")

        # Status effect engine (Lua-backed definitions)
        await self.status.initialize()
        log.info("StatusManager ready (%d effect defs loaded)", len(self.status._defs))

        await self.traps.initialize()
        log.info("Trap system ready (%d trap defs loaded)", len(self.traps._defs))

        await self.pets.initialize()
        log.info("Pet system ready")

        await self.spell_summons.initialize()
        log.info("Spell summon system ready")

        # Commands
        self.commands.register_default_commands()
        log.info("Command router ready (%d commands)", self.commands.command_count)

        # Training web portal
        self.training_web = TrainingWebServer(self)
        self.training_web.start()

        # Character creation web portal
        self.char_web = CharacterCreatorWebServer(self)
        self.char_web.start()

        # Pet shop / companion web portal
        self.pet_web = PetWebServer(self)
        self.pet_web.start()
        self._loop = asyncio.get_event_loop()

        # Boot real-time sync server (port 4902)
        log.info("Initialising real-time sync server...")
        await self.sync_server.initialize()

        # TCP
        self._tcp_server = await asyncio.start_server(
            self._handle_connection, self.host, self.port
        )
        log.info("TCP server listening on %s:%d", self.host, self.port)

        self.running = True
        log.info("Server is ONLINE.")
        log.info("=" * 60)

        await asyncio.gather(
            self.game_loop.run(),
            self._tcp_server.serve_forever(),
            self._autosave_loop(),
        )

    async def _autosave_loop(self):
        """Safety-net auto-save. Most saves happen in real-time via event handlers."""
        while self.running:
            await asyncio.sleep(AUTOSAVE_INTERVAL)
            if not self.running:
                break
            playing = self.sessions.playing()
            if playing and self.db:
                wound_bridge = getattr(self, 'wound_bridge', None)
                if wound_bridge:
                    for session in playing:
                        try:
                            wound_bridge.save_wounds_now(session)
                        except Exception as _e:
                            log.debug("Autosave wound flush failed for %s: %s",
                                      getattr(session, 'character_name', 'unknown'), _e)
                saved = self.db.save_all_characters(playing)
                if saved > 0:
                    log.debug("Safety-net auto-save: %d character(s).", saved)

    async def _handle_connection(self, reader, writer):
        addr     = writer.get_extra_info("peername")
        sockname = writer.get_extra_info("sockname")
        log.info("New connection from %s:%d", addr[0], addr[1])
        session = self.sessions.create_session(reader, writer, addr)
        # Store the IP the client used to reach us — used to build browser URLs
        # so each player's browser opens on their own machine at the right address.
        session.server_ip = sockname[0] if sockname else "127.0.0.1"

        try:
            await session.send(self._welcome_banner())
            await session.send("\r\n  1. Login to existing account")
            await session.send("\r\n  2. Create new account")
            await session.send("\r\n\r\nChoice (1-2): ")
            session.state = "main_menu"

            while self.running and session.connected:
                # NO TIMEOUT - players can AFK as long as they want
                data = await reader.readline()
                if not data:
                    break
                line = data.decode("utf-8", errors="replace").strip()
                if line:
                    session.last_input_time = time.time()
                    await self._process_input(session, line)

        except (ConnectionResetError, BrokenPipeError):
            log.info("Connection lost: %s:%d", addr[0], addr[1])
        except Exception as e:
            log.error("Session error: %s", e, exc_info=True)
        finally:
            self.sessions.remove_session(session)
            writer.close()

    async def _process_input(self, session, raw_input):
        state = session.state

        if state == "main_menu":
            await self._handle_main_menu(session, raw_input)
        elif state == "account_login_user":
            await self._handle_account_login_user(session, raw_input)
        elif state == "account_login_pass":
            await self._handle_account_login_pass(session, raw_input)
        elif state == "account_create_user":
            await self._handle_account_create_user(session, raw_input)
        elif state == "account_create_pass":
            await self._handle_account_create_pass(session, raw_input)
        elif state == "account_create_pass2":
            await self._handle_account_create_pass2(session, raw_input)
        elif state == "character_select":
            await self._handle_character_select(session, raw_input)
        elif state == "web_creating":
            await self._handle_web_creating(session, raw_input)
        elif state.startswith("create_"):
            await self.char_creator.handle_input(session, raw_input)
        elif state == "playing":
            await self.commands.handle(session, raw_input)
        else:
            await session.send_line("Unknown state. Type something.")

    # ===== MAIN MENU =====
    async def _handle_main_menu(self, session, choice):
        c = choice.strip()
        if c == "1":
            session.state = "account_login_user"
            await session.send("\r\nUsername: ")
        elif c == "2":
            session.state = "account_create_user"
            await session.send_line("\r\n  CREATE NEW ACCOUNT")
            await session.send_line("  Usernames must be 3-20 characters, alphanumeric.")
            await session.send("\r\nChoose a username: ")
        else:
            await session.send("Enter 1 or 2: ")

    # ===== ACCOUNT LOGIN =====
    async def _handle_account_login_user(self, session, username):
        session._creation_data = {"login_username": username.strip()}
        session.state = "account_login_pass"
        await session.send("Password: ")

    async def _handle_account_login_pass(self, session, password):
        username = session._creation_data.get("login_username", "")

        if not self.db:
            await session.send_line("Database unavailable. Cannot login.")
            session.state = "main_menu"
            await session.send("Choice (1-2): ")
            return

        result = self.db.authenticate(username, password)

        if result == "banned":
            await session.send_line("\r\nThis account has been banned.")
            session.disconnect()
            return

        if result is None:
            await session.send_line("\r\nInvalid username or password.")
            session.state = "main_menu"
            await session.send("\r\n  1. Login to existing account")
            await session.send("\r\n  2. Create new account")
            await session.send("\r\n\r\nChoice (1-2): ")
            return

        # Login success
        session.account_id = result["id"]
        session.account_data = result
        await session.send_line("\r\nWelcome back, " + username + "!")
        await self._show_character_select(session)

    # ===== ACCOUNT CREATION =====
    async def _handle_account_create_user(self, session, username):
        username = username.strip()
        if len(username) < 3 or len(username) > 20 or not username.isalnum():
            await session.send("Invalid. 3-20 alphanumeric characters: ")
            return
        session._creation_data = {"new_username": username}
        session.state = "account_create_pass"
        await session.send("Choose a password: ")

    async def _handle_account_create_pass(self, session, password):
        if len(password) < 4:
            await session.send("Password must be at least 4 characters: ")
            return
        session._creation_data["new_password"] = password
        session.state = "account_create_pass2"
        await session.send("Confirm password: ")

    async def _handle_account_create_pass2(self, session, password):
        if password != session._creation_data.get("new_password"):
            await session.send_line("Passwords don't match! Try again.")
            session.state = "account_create_pass"
            await session.send("Choose a password: ")
            return

        username = session._creation_data["new_username"]

        if not self.db:
            await session.send_line("Database unavailable. Cannot create account.")
            session.state = "main_menu"
            await session.send("Choice (1-2): ")
            return

        account_id = self.db.create_account(username, password)
        if account_id is None:
            await session.send_line("Username '" + username + "' already exists!")
            session.state = "account_create_user"
            await session.send("Choose a different username: ")
            return

        session.account_id = account_id
        await session.send_line("\r\nAccount '" + username + "' created successfully!")
        await self._show_character_select(session)

    # ===== CHARACTER SELECT =====
    async def _show_character_select(self, session):
        characters = []
        if self.db:
            characters = self.db.get_characters_for_account(session.account_id)

        session._creation_data["characters"] = characters
        session.state = "character_select"

        if characters:
            await session.send_line("\r\n  YOUR CHARACTERS:\r\n")
            for i, char in enumerate(characters, 1):
                await session.send_line(
                    "  " + str(i) + ". " + char["name"].ljust(20) + " Level " + str(char["level"])
                )
            await session.send_line("\r\n  " + str(len(characters) + 1) + ". Create new character")
            await session.send("\r\nEnter choice (1-" + str(len(characters) + 1) + "): ")
        else:
            await session.send_line("\r\n  You have no characters yet. Let's create one!")
            await self._launch_web_creator(session)

    async def _handle_character_select(self, session, choice):
        characters = session._creation_data.get("characters", [])
        try:
            idx = int(choice.strip())
        except ValueError:
            await session.send("Enter a number: ")
            return

        if idx == len(characters) + 1:
            await self._launch_web_creator(session)
            return

        if idx < 1 or idx > len(characters):
            await session.send("Enter 1-" + str(len(characters) + 1) + ": ")
            return

        # Load selected character
        char = characters[idx - 1]
        char_data = self.db.load_character(char["id"]) if self.db else None

        if char_data:
            session.load_from_db(char_data)
            apply_mana_max_recalc(session, self)
        else:
            session.character_name = char["name"]
            session.character_id = char["id"]

        session.state = "playing"

        # Generate real-time sync token and deliver silently to client
        if self.db and session.character_id:
            try:
                from server.core.sync.sync_auth import generate_token
                _sync_token = generate_token(self.db, session.character_id)
                _sync_port  = int(self.config.get("sync.port", 4902))
                self.sync_server.cache_token(session.character_id, _sync_token)
                # Null-byte delimited control line — client strips it, never displays
                await session.send_line(f"\x00SYNC:{_sync_token}:{_sync_port}\x00")
            except Exception as _e:
                log.warning("Failed to generate sync token: %s", _e)

        # Place in saved room
        room_id = char_data.get("current_room_id", 221) if char_data else 221
        room = self.world.get_room(room_id)
        if not room:
            room = self.world.get_room(221)

        town = (getattr(room, "zone_name", "") or (room.zone.name if room and room.zone else "")) or "the world"

        await session.send_line("\r\n" + "=" * 55)
        await session.send_line(colorize(
            "  Welcome back, " + session.character_name + "!",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "  Level " + str(session.level) + " in " + town,
            TextPresets.SYSTEM
        ))
        await session.send_line("=" * 55 + "\r\n")

        session.current_room = room
        self.world.add_player_to_room(session, room.id)

        # Load inventory from DB
        if self.db and session.character_id:
            restore_inventory_state(self, session)
            load_techniques_for_session(session, self.db)
            await reconcile_techniques_for_session(session, self, notify=False)
            load_combat_maneuvers_for_session(session, self.db)
            load_unlocks_for_session(session, self.db)
            self.hotbar.load_for_session(session)
            if getattr(self, "wound_bridge", None):
                await self.wound_bridge.load_wounds(session)

        await self.commands.handle(session, "look")
        if getattr(self, "guild", None):
            try:
                await self.guild.maybe_issue_rogue_auto_invite(session, source="login")
            except Exception as _guild_err:
                log.debug("Rogue auto-invite login check failed for %s: %s", session.character_name, _guild_err)

        # ── Event announcements on login ──────────────────────────────────────
        # Show after LOOK so the banner doesn't scroll away immediately
        if hasattr(self, 'events'):
            try:
                announcement = self.events.get_login_announcement()
                if announcement:
                    await self._send_event_announcement(session, announcement)
            except Exception as _ev_err:
                log.debug("Event announcement error: %s", _ev_err)

        # Resume tutorial if character is still in tutorial
        if not session.tutorial_complete and room and is_tutorial_room_id(room.id):
            await self.tutorial.resume_tutorial(session)

        if getattr(self, "pets", None):
            try:
                await self.pets.on_login(session)
            except Exception as _pet_err:
                log.error("Pet login hook failed for %s: %s", session.character_name, _pet_err, exc_info=True)
        if getattr(self, "spell_summons", None):
            try:
                await self.spell_summons.on_player_login(session)
            except Exception as _summon_err:
                log.error("Spell summon login hook failed for %s: %s", session.character_name, _summon_err, exc_info=True)
        if getattr(self, "fake_players", None):
            try:
                self.fake_players.on_player_login(session)
            except Exception as _fake_err:
                log.error("Fake player login hook failed for %s: %s", session.character_name, _fake_err, exc_info=True)
        if getattr(self, "town_trouble", None):
            try:
                await self.town_trouble.on_player_login(session)
            except Exception as _trouble_err:
                log.error("Town trouble login hook failed for %s: %s", session.character_name, _trouble_err, exc_info=True)

    # ===== WEB CHARACTER CREATOR =====

    async def _launch_web_creator(self, session):
        """Open the browser-based character creator for this session."""
        if self.char_web:
            token = self.char_web.generate_token(session)
            url   = f"http://{session.server_ip}:8766/create?token={token}"

            await session.send_line("")
            await session.send_line("  +---------------------------------------------------------+")
            await session.send_line("  |        Character Creation is open in your browser.     |")
            await session.send_line("  |  Complete your character there, then return here.      |")
            await session.send_line("  +---------------------------------------------------------+")
            await session.send_line("")
            await session.send_line(f"  {url}")
            await session.send_line("  Type CANCEL to go back to character select.")
            await session.send("")
            session.state = "web_creating"

            await session.send_line("")
            await session.send_line("  +---------------------------------------------------------+")
            await session.send_line("  |        Character Creation is open in your browser.     |")
            await session.send_line("  |  Complete your character there, then return here.      |")
            await session.send_line("  +---------------------------------------------------------+")
            await session.send_line("")
            await session.send_line("  Type CANCEL to go back to character select.")
            await session.send("")
            session.state = "web_creating"
            session.web_char_ready = False
        else:
            # Fallback to terminal creator if web server is unavailable
            log.warning("Character creator web server not available — falling back to terminal")
            await self.char_creator.start(session)

    async def _handle_web_creating(self, session, raw_input):
        """Handle input while a player waits for web character creation to finish.
        The session advances automatically when the browser submits —
        the only valid input here is CANCEL to abort.
        """
        raw = raw_input.strip().lower()
        if raw in ("cancel", "quit", "q", "back"):
            session.state = "character_select"
            await self._show_character_select(session)
            return

        await session.send_line("")
        await session.send_line("  Character creation is open in your browser.")
        await session.send_line("  Type CANCEL to return to character select.")
        await session.send("")

    async def _finish_web_character(self, session):
        """Advance session into the world after web character creation completes."""
        await session.send_line("")
        await session.send_line("=" * 55)
        await session.send_line(
            f"  {session.character_name} enters the world...")
        await session.send_line("=" * 55)
        await session.send_line("")

        # Load inventory from DB
        if self.db and session.character_id:
            restore_inventory_state(self, session)
            load_techniques_for_session(session, self.db)
            await reconcile_techniques_for_session(session, self, notify=False)
            load_combat_maneuvers_for_session(session, self.db)
            load_unlocks_for_session(session, self.db)
            self.hotbar.load_for_session(session)

        if getattr(self, "spell_summons", None):
            try:
                await self.spell_summons.on_player_login(session)
            except Exception as _summon_err:
                log.error("Spell summon login hook failed after web create for %s: %s", session.character_name, _summon_err, exc_info=True)

        # Generate real-time sync token
        if self.db and session.character_id:
            try:
                from server.core.sync.sync_auth import generate_token
                _sync_token = generate_token(self.db, session.character_id)
                _sync_port  = int(self.config.get("sync.port", 4902))
                self.sync_server.cache_token(session.character_id, _sync_token)
                await session.send_line(f"\x00SYNC:{_sync_token}:{_sync_port}\x00")
            except Exception as _e:
                log.warning("Failed to generate sync token after web creation: %s", _e)

        # Find starting room
        race_id      = getattr(session, "race_id", 1)
        start_room_id = int(getattr(session, "starting_room_id", 0) or self.char_creator._get_default_starting_room())

        if hasattr(self, "tutorial") and self.tutorial and not getattr(session, "tutorial_complete", True):
            await self.tutorial.start_tutorial(session)
        else:
            session.state = "playing"
            room = self.world.get_room(start_room_id)
            if not room:
                room = self.world.get_room(221)
            if room:
                session.current_room = room
                self.world.add_player_to_room(session, room.id)
                await self.commands.handle(session, "look")
                # Event announcement after look (same as normal login path)
                if hasattr(self, 'events'):
                    try:
                        announcement = self.events.get_login_announcement()
                        if announcement:
                            await self._send_event_announcement(session, announcement)
                    except Exception:
                        pass
            else:
                await session.send("(Warning: starting room not found!)\r\n>")

    # ===== UTILITIES =====

    async def _send_event_announcement(self, session, announcement) -> None:
        """
        Render an event announcement cleanly.
        announcement can be a str (single block) or a list of str (pre-split lines).
        Uses simple separators — proportional fonts make fixed-width boxes look broken.
        """
        import textwrap
        SEP = "  " + "─" * 52

        # Normalise to a list of display lines
        if isinstance(announcement, list):
            lines = announcement
        else:
            lines = textwrap.wrap(str(announcement), width=60)

        await session.send_line("")
        await session.send_line(colorize(SEP, TextPresets.EXPERIENCE))
        await session.send_line("")
        for text_line in lines:
            await session.send_line(colorize(f"    {text_line}", TextPresets.EXPERIENCE))
            await session.send_line("")          # blank line after every content line
        await session.send_line(colorize(SEP, TextPresets.EXPERIENCE))
        await session.send_line("")

    def _welcome_banner(self):
        return (
            "\r\n"
            + colorize("  +================================================+", TextPresets.SYSTEM) + "\r\n"
            + colorize("  |       GemStone IV - Private Server              |", TextPresets.SYSTEM) + "\r\n"
            + colorize("  |              v0.2.0 Alpha                       |", TextPresets.SYSTEM) + "\r\n"
            + colorize("  +================================================+", TextPresets.SYSTEM) + "\r\n"
        )

    def shutdown(self):
        log.info("Shutting down server...")
        self.running = False

        # Save all characters before shutdown
        if self.db:
            playing = self.sessions.playing()
            if playing:
                wound_bridge = getattr(self, 'wound_bridge', None)
                if wound_bridge:
                    for session in playing:
                        try:
                            wound_bridge.save_wounds_now(session)
                        except Exception as _e:
                            log.debug("Shutdown wound flush failed for %s: %s",
                                      getattr(session, 'character_name', 'unknown'), _e)
                saved = self.db.save_all_characters(playing)
                log.info("Shutdown: saved %d character(s).", saved)

        for session in self.sessions.all():
            asyncio.ensure_future(
                session.send("\r\n*** Server is shutting down. ***\r\n")
            )

        if self._tcp_server:
            self._tcp_server.close()
        if getattr(self, "fake_players", None):
            try:
                self.fake_players.shutdown()
            except Exception as _fake_shutdown_err:
                log.debug("Fake player shutdown cleanup failed: %s", _fake_shutdown_err)
        if getattr(self, "creatures", None):
            try:
                self.creatures.shutdown()
            except Exception as _creature_shutdown_err:
                log.debug("Creature shutdown cleanup failed: %s", _creature_shutdown_err)
        if getattr(self, "persistence_writer", None):
            try:
                self.persistence_writer.shutdown()
            except Exception as _writer_shutdown_err:
                log.debug("Persistence writer shutdown cleanup failed: %s", _writer_shutdown_err)
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        log.info("Server stopped.")
