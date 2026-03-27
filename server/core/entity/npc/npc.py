"""
npc.py
------
NPC Entity — Non-Player Characters for the GemStone IV private server.

NPCs are defined by their capability flags.  A shopkeeper has can_shop=True.
A combat guard has can_combat=True.  A bot has everything True.  The same
class handles all of them — the manager just calls the methods that apply.

Backward-compatible with the existing NPC_TEMPLATES list in npc_data.py.
New NPCs loaded from Lua gain all extended fields automatically.

Combat compatibility:
    NPC instances are duck-type compatible with Creature for the combat engine.
    They expose .health_current, .health_max, .as_melee, .ds_melee, .attacks,
    .alive, .in_combat, .target, .status_effects, .wounds, .can_act(),
    .take_damage(), .choose_attack() so the existing CombatEngine works
    without modification.
"""

import random
import time
import logging
from server.core.protocol.colors import npc_emote, npc_speech, npc_name, colorize, TextPresets

log = logging.getLogger(__name__)

_GENERIC_DIALOGUE_DEFAULTS = {
    "the npc doesn't seem to be listening.",
    "the npc does not seem to be listening.",
}

_SERVICE_GREETING_FALLBACKS = {
    "bank": 'looks up from the ledger and inclines %s head politely.  "Banking business?"',
    "locksmith": 'glances up from a half-worked lock.  "Need something opened or repaired?"',
    "travel": 'looks up from a stack of schedules.  "Planning a journey?"',
    "healer": 'turns toward you with quiet concern.  "Are you hurt?"',
    "inn": 'offers a welcoming nod.  "Looking for a room or a meal?"',
    "guild": 'glances up from a pile of records.  "Guild business?"',
    "registrar": "adjusts a stack of forms and regards you expectantly.",
    "pawnbroker": "glances over your gear with a practiced appraiser's eye.",
    "priest": "folds %s hands and offers a solemn nod.",
}

_SERVICE_DIALOGUE_FALLBACKS = {
    "bank": {
        "deposit": "DEPOSIT places silver into your account.  WITHDRAW retrieves it, and CHECK BALANCE confirms the total.",
        "withdraw": "WITHDRAW <amount> pulls silver from your account.  WITHDRAW <amount> NOTE writes out a bank note when needed.",
        "account": "Your account balance is tracked securely.  CHECK BALANCE will tell you the current total.",
        "note": "Bank notes can be deposited directly if you are holding them.  Use DEPOSIT NOTE.",
        "default": 'The teller waits with professional patience.  "Deposit, withdraw, or check your balance?"',
    },
    "locksmith": {
        "repair": "Hold the broken pick, APPRAISE it for the quote, then pay the locksmith to repair it.",
        "box": "Hold the locked box, RING BELL for a quote, then PAY to post it to the shared locksmith queue.",
        "service": "Locksmiths quote box work with RING BELL and accept payment with PAY.  Rogues use BOXPICK to work the shared queue.",
        "pick": "I can sell picks, repair broken ones, and broker box work through the locksmith queue.",
        "default": 'The locksmith gives you a quick once-over.  "Locks, picks, or repairs?"',
    },
    "travel": {
        "travel": "I can discuss routes and local travel arrangements, but the actual travel network is not wired in here yet.",
        "airship": "Airship and route information is handled here, though the actual travel transport still needs its backend.",
        "route": "I can point you toward routes and destinations, but booking and transport still need to be implemented.",
        "default": 'The clerk smooths a schedule sheet.  "If you need route information, ask."',
    },
    "healer": {
        "heal": "I can discuss healing, but the paid healer service itself is not wired yet.",
        "injury": "For now, field treatment and herbs do the work.  Dedicated healer services still need their own backend.",
        "wound": "Your wounds will have to be handled through the healing systems already in place; healer NPC service is not live yet.",
        "default": 'The healer studies you with concern.  "If you need treatment, say so."',
    },
    "inn": {
        "room": "The inn can offer lodging and rest, though room rental and stay tracking still need a proper backend.",
        "rest": "This is a place to rest, though full inn service is not wired yet.",
        "food": "Meals and lodging belong here, but only the social side is live at the moment.",
        "default": 'The innkeeper waits patiently.  "Need a room, some food, or a place to rest?"',
    },
    "guild": {
        "guild": "Guild administration exists here, but the full guild backend still needs to be hooked up.",
        "join": "Joining and rank handling will need the proper guild system before I can process it.",
        "bounty": "Taskmasters can register you, issue cull, gem, skin, forage, heirloom, bandit, boss, escort, and rescue contracts, review rank, record check-ins, and close completed bounties.",
        "default": 'The clerk gives you a measuring look.  "Guild business?"',
    },
    "registrar": {
        "register": "Registration, surnames, citizenship, and deed work belong here, but the paperwork system itself is not live yet.",
        "citizenship": "Citizenship processing still needs the registrar backend before it can function properly.",
        "surname": "Surname handling belongs to the registrar, but that backend is still pending.",
        "deed": "Property and deed records will need a dedicated registrar system before they can be processed.",
        "default": 'The registrar taps a stack of forms.  "Registration or records?"',
    },
    "pawnbroker": {
        "sell": "Present what you want appraised or sold.  Pawnbroker behavior follows the existing shop flow where configured.",
        "buy": "Available stock depends on what the pawnbroker has on offer in this shop.",
        "appraise": "APPRAISE lets you hear an offer before you SELL an item.",
        "default": "The pawnbroker looks over your belongings with open interest.",
    },
    "priest": {
        "arkati": "Temple and Arkati guidance belongs here, though any deeper religious services still need their own backend.",
        "prayer": "The priest murmurs a few measured words about faith and devotion.",
        "death": "Death and afterlife guidance can be discussed here, though the service backend is still limited.",
        "default": "The priest offers a solemn, patient look.",
    },
}


class NPC:
    """Represents a single NPC instance in the game world."""

    _next_id = 50000  # NPC IDs start at 50000

    def __init__(self, template: dict):
        NPC._next_id += 1
        self.id          = NPC._next_id
        self.template_id = template["template_id"]
        self.lua_file    = template.get("lua_file", None)
        self.lua_module  = template.get("lua_module", None)

        # ── Identity ──────────────────────────────────────────────────────────
        self.name        = template["name"]
        self.article     = template.get("article", "")
        self.title       = template.get("title", "")
        self.description = template.get("description", "You see nothing unusual.")
        self.room_id     = template.get("room_id", 0)
        self.home_room_id = template.get("home_room_id", self.room_id)

        # Creature-compat alias
        self.current_room_id = self.room_id

        # ── Capabilities ──────────────────────────────────────────────────────
        self.can_combat   = bool(template.get("can_combat",   False))
        self.can_shop     = bool(template.get("can_shop",     False))
        self.can_wander   = bool(template.get("can_wander",   False))
        self.can_emote    = bool(template.get("can_emote",    False))
        self.can_chat     = bool(template.get("can_chat",     False))
        self.can_loot     = bool(template.get("can_loot",     False))
        self.is_guild     = bool(template.get("is_guild",     False))
        self.is_quest     = bool(template.get("is_quest",     False))
        self.is_house     = bool(template.get("is_house",     False))
        self.is_bot       = bool(template.get("is_bot",       False))
        self.is_invasion  = bool(template.get("is_invasion",  False))

        # Legacy role field (kept for backward compat with npc_data.py templates)
        if self.can_shop:
            self.role = "shopkeeper"
        else:
            self.role = template.get("role", "townsfolk")

        # ── Combat stats ──────────────────────────────────────────────────────
        self.level        = int(template.get("level", 1))
        self.health_max   = int(template.get("hp", 100))
        self.health_current = self.health_max
        self.as_melee     = int(template.get("as_melee", 50))
        self.ds_melee     = int(template.get("ds_melee", 30))
        self.ds_ranged    = int(template.get("ds_ranged", 20))
        self.td           = int(template.get("td", 10))
        self.armor_asg    = int(template.get("armor_asg", 5))
        self.body_type    = template.get("body_type", "biped")
        self.damage_type  = "crush"
        self.aggressive   = bool(template.get("aggressive", False))
        self.unkillable   = bool(template.get("unkillable", False))
        self.respawn_seconds = int(template.get("respawn_seconds", 600))
        self.attacks      = template.get("attacks", [])
        self.stance       = "neutral"

        # Combat state (creature-compat)
        self.alive        = True
        self.is_alive     = True
        self.in_combat    = False
        self.target       = None
        self.roundtime_end = 0.0
        self.death_time   = 0.0
        self.wounds: dict = {}
        self.status_effects: dict = {}

        # ── Shop ──────────────────────────────────────────────────────────────
        self.shop_id      = template.get("shop_id", None)

        # ── Dialogue ──────────────────────────────────────────────────────────
        self.dialogues    = template.get("dialogues", {})
        self.greeting     = template.get("greeting", None)

        # ── Patrol / wander ───────────────────────────────────────────────────
        self.patrol_rooms   = template.get("patrol_rooms", [])
        self.patrol_index   = 0
        self.wander_chance  = float(template.get("wander_chance", 0.0))
        self.move_interval  = int(template.get("move_interval", 30))
        self.last_move_time = 0.0

        # ── Shift system ──────────────────────────────────────────────────────
        self.shift_id     = template.get("shift_id", None)
        self.shift_phase  = int(template.get("shift_phase", 0))
        self.spawn_at_start = bool(template.get("spawn_at_start", True))

        # ── Rare spawn ────────────────────────────────────────────────────────
        self.rare_spawn   = bool(template.get("rare_spawn", False))
        self.spawn_chance = float(template.get("spawn_chance", 1.0))

        # ── Ambient emotes ────────────────────────────────────────────────────
        self.ambient_emotes  = template.get("ambient_emotes", [])
        self.ambient_chance  = float(template.get("ambient_chance", 0.03))
        self.emote_cooldown  = int(template.get("emote_cooldown", 45))
        self.last_emote_time = 0.0

        # ── Chat ──────────────────────────────────────────────────────────────
        self.chat_lines      = template.get("chat_lines", [])
        self.chat_interval   = int(template.get("chat_interval", 120))
        self.chat_chance     = float(template.get("chat_chance", 0.12))
        # Stagger first chatter so rooms don't erupt immediately after reloads.
        self.last_chat_time  = time.time() - random.uniform(0, self.chat_interval * 0.25)

        # ── Loot ──────────────────────────────────────────────────────────────
        self.loot_silver  = bool(template.get("loot_silver", True))
        self.loot_gems    = bool(template.get("loot_gems", False))
        self.loot_items   = bool(template.get("loot_items", False))
        self.loot_radius  = int(template.get("loot_radius", 0))

        # ── Guild ─────────────────────────────────────────────────────────────
        self.guild_id     = template.get("guild_id", None)

        # ── Bot ───────────────────────────────────────────────────────────────
        self.bot_hunt       = bool(template.get("bot_hunt", False))
        self.bot_hunt_rooms = template.get("bot_hunt_rooms", [])
        self.bot_rest_room  = int(template.get("bot_rest_room", 0))
        self.bot_hp_flee    = float(template.get("bot_hp_flee", 0.25))
        self.bot_chat_world = bool(template.get("bot_chat_world", False))

        # ── Invasion ──────────────────────────────────────────────────────────
        self.invasion_zone = template.get("invasion_zone", None)
        self.invasion_side = template.get("invasion_side", "enemy")

        # ── Hook manifest ─────────────────────────────────────────────────────
        # List of hook names defined in the Lua file.
        # The Lua engine checks this before trying to call a hook.
        self.hooks: list = template.get("hooks", [])

        # ── Lua table reference (set by manager after Lua load) ───────────────
        # If the Lua engine loads this NPC's file, the returned Lua table
        # is stored here so hooks can be called at runtime.
        self._lua_table = None

    # ── Display ───────────────────────────────────────────────────────────────

    @property
    def display_name(self) -> str:
        if self.title:
            return f"{self.name} {self.title}"
        return self.name

    @property
    def full_name(self) -> str:
        return self.display_name

    @property
    def full_name_with_level(self) -> str:
        """Creature-compat property for combat engine display."""
        return f"{self.display_name} [Level {self.level}]"

    # ── Creature-compat combat interface ─────────────────────────────────────

    @property
    def is_dead(self) -> bool:
        return not self.alive or self.health_current <= 0

    @property
    def is_stunned(self) -> bool:
        effects = getattr(self, "status_effects", {}) or {}
        se = effects.get("stunned")
        if se is None:
            return False
        if hasattr(se, "active"):
            return se.active
        if isinstance(se, dict):
            return time.time() < se.get("expires", 0)
        return False

    def can_act(self) -> bool:
        """Creature-compat: can this NPC take a combat action right now?"""
        if self.is_dead:
            return False
        if self.is_stunned:
            return False
        if self.get_roundtime() > 0:
            return False
        return True

    def get_roundtime(self) -> float:
        return max(0.0, self.roundtime_end - time.time())

    def set_roundtime(self, seconds: float):
        self.roundtime_end = time.time() + seconds

    def take_damage(self, amount: int) -> int:
        """Creature-compat damage application.  Respects unkillable flag."""
        if self.unkillable:
            return 0
        actual = min(amount, self.health_current)
        self.health_current -= actual
        if self.health_current <= 0:
            self.health_current = 0
            self.alive     = False
            self.is_alive  = False
            self.in_combat = False
            self.target    = None
            self.death_time = time.time()
            self.wounds = {}
            self.status_effects = {}
        return actual

    def heal(self, amount: int):
        self.health_current = min(self.health_current + amount, self.health_max)

    def choose_attack(self) -> dict:
        """Creature-compat: pick a random attack."""
        if not self.attacks:
            return {
                "name": "attack", "as": self.as_melee,
                "damage_type": "crush",
                "verb_first": "attacks you",
                "verb_third": "attacks {target}",
                "roundtime": 5,
            }
        return random.choice(self.attacks)

    def apply_wound(self, location: str, crit_rank: int) -> int:
        """Creature-compat wound tracking."""
        new_sev = min(5, (crit_rank + 1) // 2)
        current = self.wounds.get(location, 0)
        if new_sev > current:
            self.wounds[location] = new_sev
        return self.wounds.get(location, new_sev)

    def get_melee_as(self, attack=None) -> int:
        base = attack.get("as", self.as_melee) if attack else self.as_melee
        if self.health_max > 0:
            hp_pct = self.health_current / self.health_max
            if hp_pct < 0.75:
                base -= int((0.75 - hp_pct) / 0.75 * 30)
        return max(0, base)

    def get_melee_ds(self) -> int:
        ds = self.ds_melee
        if self.health_max > 0:
            hp_pct = self.health_current / self.health_max
            if hp_pct < 0.75:
                ds -= int((0.75 - hp_pct) / 0.75 * 40)
        return max(0, ds)

    # ── Dialogue ──────────────────────────────────────────────────────────────

    def get_dialogue(self, keyword: str) -> str | None:
        kw = keyword.lower().strip()
        if kw in self.dialogues:
            return self.dialogues[kw]
        for key in self.dialogues:
            if key != "default" and key.startswith(kw):
                return self.dialogues[key]
        for key, response in self.dialogues.items():
            if key != "default" and key in kw:
                return response
        service_response = self.get_service_dialogue(kw)
        if service_response:
            return service_response
        return self.dialogues.get("default", None)

    def _service_text(self) -> str:
        pieces = [
            self.template_id or "",
            self.name or "",
            self.title or "",
            self.description or "",
            " ".join(self.dialogues.keys()) if self.dialogues else "",
        ]
        return " ".join(pieces).lower()

    def get_service_tags(self) -> set[str]:
        tags: set[str] = set()
        text = self._service_text()

        if self.can_shop and self.shop_id:
            tags.add("shop")
        if self.is_guild or self.guild_id:
            tags.add("guild")
        if "locksmith" in text or "lockpick" in text:
            tags.add("locksmith")
        if "bank teller" in text or "bank clerk" in text or ("bank" in text and "teller" in text):
            tags.add("bank")
        if "healer" in text or "empath" in text:
            tags.add("healer")
        if "travel clerk" in text or "travel" in text or "airship" in text or "route" in text:
            tags.add("travel")
        if "innkeeper" in text or ("inn" in text and "keeper" in text):
            tags.add("inn")
        if "guild" in text or "guildmaster" in text or "bounty" in text:
            tags.add("guild")
        if "registrar" in text or "citizenship" in text or "surname" in text or "deed" in text:
            tags.add("registrar")
        if "pawnbroker" in text:
            tags.add("pawnbroker")
        if "priest" in text or "acolyte" in text or "arkati" in text or "temple" in text:
            tags.add("priest")
        return tags

    def matches_service(self, tag: str) -> bool:
        return tag in self.get_service_tags()

    def get_greeting_text(self) -> str | None:
        if self.greeting:
            return self.greeting

        desc = (self.description or "").lower()
        pronoun = "his" if any(word in desc for word in (" his ", " he ")) else "her"
        for tag in ("locksmith", "bank", "travel", "healer", "inn", "guild", "registrar", "pawnbroker", "priest"):
            if self.matches_service(tag):
                template = _SERVICE_GREETING_FALLBACKS.get(tag)
                if template:
                    return template % pronoun if "%s" in template else template
        return None

    def get_service_dialogue(self, keyword: str) -> str | None:
        kw = (keyword or "").lower().strip()
        default_dialogue = (self.dialogues.get("default", "") or "").strip().lower()
        generic_default = default_dialogue in _GENERIC_DIALOGUE_DEFAULTS

        for tag in ("locksmith", "bank", "travel", "healer", "inn", "guild", "registrar", "pawnbroker", "priest"):
            if not self.matches_service(tag):
                continue
            fallback = _SERVICE_DIALOGUE_FALLBACKS.get(tag, {})
            if not fallback:
                continue

            for key, response in fallback.items():
                if key == "default":
                    continue
                if kw == key or key.startswith(kw) or key in kw:
                    return response

            if generic_default or not self.dialogues:
                return fallback.get("default")
        return None

    def get_talk_response(self, server, player, keyword: str) -> str | None:
        if self.has_hook("on_player_talk") and self._lua_table:
            lua = getattr(server, "lua", None)
            engine = getattr(lua, "engine", None) if lua else None
            if engine and engine.available:
                raw = engine.call_hook(self._lua_table, "on_player_talk", player, keyword or "")
                raw = engine.lua_to_python(raw)
                if isinstance(raw, str) and raw.strip():
                    return raw.strip()
                if isinstance(raw, dict):
                    for field in ("response", "message", "text"):
                        value = raw.get(field)
                        if isinstance(value, str) and value.strip():
                            return value.strip()

        return self.get_dialogue(keyword or "")

    # ── Ambient emotes ────────────────────────────────────────────────────────

    def get_ambient_emote(self) -> str | None:
        if not self.ambient_emotes or not self.can_emote:
            return None
        now = time.time()
        if now - self.last_emote_time < self.emote_cooldown:
            return None
        if random.random() > self.ambient_chance:
            return None
        self.last_emote_time = now
        raw = random.choice(self.ambient_emotes).replace("{name}", self.name)
        return npc_emote(raw)

    # ── Chat ──────────────────────────────────────────────────────────────────

    def get_chat_line(self) -> str | None:
        if not self.chat_lines or not self.can_chat:
            return None
        now = time.time()
        if now - self.last_chat_time < self.chat_interval:
            return None
        if random.random() > self.chat_chance:
            return None
        self.last_chat_time = now
        line = random.choice(self.chat_lines).replace("{name}", self.name)
        return npc_speech(self.display_name, line)

    # ── Patrol ────────────────────────────────────────────────────────────────

    def is_ready_to_move(self) -> bool:
        return (self.can_wander and
                bool(self.patrol_rooms) and
                time.time() - self.last_move_time >= self.move_interval)

    def get_next_patrol_room(self) -> int | None:
        if not self.patrol_rooms:
            return None
        self.patrol_index = (self.patrol_index + 1) % len(self.patrol_rooms)
        return self.patrol_rooms[self.patrol_index]

    def record_move(self):
        self.last_move_time = time.time()
        self.current_room_id = self.room_id  # keep in sync

    # ── Hook helpers ──────────────────────────────────────────────────────────

    def has_hook(self, hook_name: str) -> bool:
        return hook_name in self.hooks

    def __repr__(self) -> str:
        status = "alive" if self.alive else "dead"
        caps = [k for k in ("can_combat", "can_shop", "can_wander",
                             "is_bot", "is_invasion") if getattr(self, k)]
        return (f"NPC({self.id}, {self.template_id!r}, "
                f"HP:{self.health_current}/{self.health_max}, "
                f"{status}, [{', '.join(caps)}])")
