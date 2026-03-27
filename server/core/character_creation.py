"""
Character Creation Flow — GemStone IV Clone
All data sourced from https://gswiki.play.net/Statistic

Stat allocation: 640 base points + 20 prime requisite bonus = 660 total.
Prime requisite stats start at 30 (not 20), giving them a free +10 each.
Each stat range: 20-100 (primes: 30-100).
Bonus formula: floor((stat - 50) / 2)
PTP = 25 + [(STR+CON+DEX+AGI + (AUR+DIS)/2) / 20]  (primes doubled)
MTP = 25 + [(LOG+INT+WIS+INF + (AUR+DIS)/2) / 20]  (primes doubled)

ALL game data (races, professions, appearance, starter gear) is loaded
exclusively from Lua.  There are no Python fallbacks.  If a Lua file is
missing or broken, character creation will log CRITICAL and fail loudly
rather than silently using stale data.
"""

import logging
import math
from server.core.commands.player.inventory import restore_inventory_state

log = logging.getLogger(__name__)


def _require_lua_data(server, getter_name: str, data_key: str = None):
    """
    Load data from Lua.  Log CRITICAL and raise RuntimeError if unavailable.
    There are no fallbacks — fix the Lua file if this fires.
    """
    lua = getattr(server, "lua", None)
    if lua is None:
        log.critical(
            "CHARACTER CREATION: LuaManager not available. "
            "Cannot load %s. Check server startup.", getter_name
        )
        raise RuntimeError(f"Lua unavailable — cannot load {getter_name}")

    getter = getattr(lua, getter_name, None)
    if getter is None:
        log.critical("CHARACTER CREATION: LuaManager has no method %r", getter_name)
        raise RuntimeError(f"LuaManager missing method {getter_name}")

    data = getter()
    if data is None:
        log.critical(
            "CHARACTER CREATION: %s() returned None. "
            "The Lua file failed to load or parse. "
            "Check scripts/data/ for errors.", getter_name
        )
        raise RuntimeError(f"{getter_name}() returned None — Lua data missing")

    if data_key:
        sub = data.get(data_key)
        if not sub:
            log.critical(
                "CHARACTER CREATION: %s()[%r] is empty. "
                "Check the Lua file.", getter_name, data_key
            )
            raise RuntimeError(f"{getter_name}()[{data_key!r}] is empty")
        return sub

    return data


def _load_appearance_data(server):
    """Load appearance data from Lua. Raises if unavailable — no fallback."""
    return _require_lua_data(server, "get_appearance")


# ── Mathematical / system constants ───────────────────────────────────────────
# These are computation constants used by calc_tp and stat allocation.
# They are NOT game data — do not add race/profession/appearance data here.

TOTAL_BASE_POINTS = 640
PRIME_BONUS       = 10
TOTAL_STAT_POINTS = 660
STAT_MIN          = 20
STAT_MAX          = 100
PRIME_MIN         = 30
NUM_STATS         = 10

# Stat index ordering constants — used by the Python allocation engine.
# Order: STR CON DEX AGI DIS AUR LOG INT WIS INF
STAT_NAMES   = ["Strength", "Constitution", "Dexterity", "Agility", "Discipline",
                "Aura", "Logic", "Intuition", "Wisdom", "Influence"]
STAT_ABBREVS = ["STR", "CON", "DEX", "AGI", "DIS", "AUR", "LOG", "INT", "WIS", "INF"]
STAT_KEYS    = ["strength", "constitution", "dexterity", "agility", "discipline",
                "aura", "logic", "intuition", "wisdom", "influence"]
STAT_DESCRIPTIONS = {
    0: "Physical power. Affects melee AS, carrying capacity before encumbrance.",
    1: "Durability. Determines max HP, disease resistance, critical hit defense.",
    2: "Hand-eye coordination. Lockpicking, pickpocketing, ranged aiming, dual wield.",
    3: "Grace and nimbleness. Directly affects DS, dodge, balance, initiative.",
    4: "Force of will. Experience absorption before rest, mental attack resistance.",
    5: "Spiritual/elemental connection. Spirit points, elemental TD/CS, mana (casters).",
    6: "Reasoning ability. Experience absorption, magic item activation, arcane TD/CS.",
    7: "Instinctive awareness. Trap detection, perception, stalking, ambush.",
    8: "Pragmatism and spiritual insight. Spiritual TD/CS, mana for semis.",
    9: "Charisma and persuasion. Trading, mind-affecting magic, social skills.",
}


def stat_bonus(raw_stat):
    """Convert raw stat (20-100) to bonus. Formula: floor((stat-50)/2)"""
    return math.floor((raw_stat - 50) / 2)


def calc_tp(stats, prof_id, primes=None):
    """Calculate Physical and Mental training points per level.

    PTP = 25 + [(STR+CON+DEX+AGI + (AUR+DIS)/2) / 20]  (primes doubled)
    MTP = 25 + [(LOG+INT+WIS+INF + (AUR+DIS)/2) / 20]  (primes doubled)

    primes: two 0-based stat indices supplied by caller from Lua data.
    """
    if primes is None:
        primes = (0, 1)

    def effective(idx):
        val = stats[idx]
        return val * 2 if idx in primes else val

    hybrid_half = (effective(5) + effective(4)) / 2
    phys_sum    = effective(0) + effective(1) + effective(2) + effective(3) + hybrid_half
    ment_sum    = effective(6) + effective(7) + effective(8) + effective(9) + hybrid_half

    ptp = 25 + math.floor(phys_sum / 20)
    mtp = 25 + math.floor(ment_sum / 20)
    return ptp, mtp


class CharacterCreator:
    """Handles the multi-step character creation flow."""

    def __init__(self, server):
        self.server = server
        self._lua_data_cache = {}

    def _lua(self):
        """Return loaded Lua appearance data. Raises if unavailable."""
        return _load_appearance_data(self.server)

    def _get_races(self):
        return _require_lua_data(self.server, "get_races", "races")

    def _get_race_stat_mods(self):
        return _require_lua_data(self.server, "get_races", "stat_mods")

    def _get_race_starting_rooms(self):
        return _require_lua_data(self.server, "get_races", "starting_rooms")

    def _get_race_town_names(self):
        return _require_lua_data(self.server, "get_races", "town_names")

    def _get_starter_towns(self):
        return _require_lua_data(self.server, "get_races", "starter_towns")

    def _get_default_starting_room(self):
        data = _require_lua_data(self.server, "get_races")
        return int(data.get("default_starting_room") or 221)

    def _get_professions(self):
        return _require_lua_data(self.server, "get_professions", "professions")

    def _get_profession_stats(self):
        return _require_lua_data(self.server, "get_professions", "profession_stats")

    def _get_prime_requisites(self):
        return _require_lua_data(self.server, "get_professions", "prime_requisites")

    async def handle_input(self, session, raw_input):
        step = session.state
        if step == "create_name":
            await self._step_name(session, raw_input)
        elif step == "create_gender":
            await self._step_gender(session, raw_input)
        elif step == "create_race":
            await self._step_race(session, raw_input)
        elif step == "create_profession":
            await self._step_profession(session, raw_input)
        elif step == "create_culture":
            await self._step_culture(session, raw_input)
        elif step == "create_stats":
            await self._step_stats(session, raw_input)
        elif step == "create_hair_color":
            await self._step_hair_color(session, raw_input)
        elif step == "create_hair_style":
            await self._step_hair_style(session, raw_input)
        elif step == "create_eye_color":
            await self._step_eye_color(session, raw_input)
        elif step == "create_skin_tone":
            await self._step_skin_tone(session, raw_input)
        elif step == "create_height":
            await self._step_height(session, raw_input)
        elif step == "create_age":
            await self._step_age(session, raw_input)
        elif step == "create_confirm":
            await self._step_confirm(session, raw_input)

    async def start(self, session):
        session._creation_data = {}
        session.state = "create_name"
        await session.send_line("\r\n" + "=" * 55)
        await session.send_line("          CHARACTER CREATION")
        await session.send_line("=" * 55)
        await session.send_line("\r\nLet us begin by choosing a name for your character.")
        await session.send_line("Names must be 2-20 letters, no numbers or spaces.")
        await session.send("\r\nWhat name do you wish to be known by? ")

    # --- Step 1: Name ---
    async def _step_name(self, session, name):
        name = name.strip().capitalize()
        if len(name) < 2 or len(name) > 20 or not name.isalpha():
            await session.send("Invalid name. Use 2-20 letters only: ")
            return
        if self.server.db and self.server.db.character_name_exists(name):
            await session.send_line(f"The name '{name}' is already taken. Choose another.")
            await session.send("What name do you wish to be known by? ")
            return
        session._creation_data["name"] = name
        session.character_name = name
        session.state = "create_gender"
        await session.send_line(f"\r\n  Name: {name}")
        await session.send_line("\r\nWhat is your gender?")
        await session.send_line("  1. Female")
        await session.send_line("  2. Male")
        await session.send("\r\nEnter choice (1-2): ")

    # --- Step 2: Gender ---
    async def _step_gender(self, session, choice):
        c = choice.strip().lower()
        if c in ("1", "f", "female"):
            session._creation_data["gender"] = "female"
        elif c in ("2", "m", "male"):
            session._creation_data["gender"] = "male"
        else:
            await session.send("Please enter 1 or 2: ")
            return
        session.gender = session._creation_data["gender"]
        session.state = "create_race"
        await self._show_race_menu(session)

    # --- Step 3: Race ---
    async def _show_race_menu(self, session):
        races = self._get_races()
        race_stat_mods = self._get_race_stat_mods()
        start_rooms = self._get_race_starting_rooms()
        town_names = self._get_race_town_names()
        await session.send_line("\r\nChoose your race:\r\n")
        for i, race in enumerate(races, 1):
            await session.send_line(f"  {i:>2}. {race['name']:<18} - {race['desc']}")
            mods = race_stat_mods.get(race["id"], [0]*10)
            parts = []
            for j, mod in enumerate(mods):
                if mod != 0:
                    sign = "+" if mod > 0 else ""
                    parts.append(f"{STAT_ABBREVS[j]} {sign}{mod}")
            mod_str = ", ".join(parts) if parts else "none"
            start_room = int(start_rooms.get(race["id"], self._get_default_starting_room()) or self._get_default_starting_room())
            await session.send_line(f"      Starts in: {town_names.get(start_room, 'Unknown')}   Mods: {mod_str}")
        await session.send(f"\r\nEnter choice (1-{len(races)}): ")

    async def _step_race(self, session, choice):
        races = self._get_races()
        try:
            idx = int(choice.strip())
            if idx < 1 or idx > len(races):
                raise ValueError
        except ValueError:
            await session.send(f"Enter a number 1-{len(races)}: ")
            return
        race = races[idx - 1]
        start_room = int(self._get_race_starting_rooms().get(race["id"], self._get_default_starting_room()) or self._get_default_starting_room())
        start_town = self._get_race_town_names().get(start_room, "Unknown")
        session._creation_data["race_id"] = race["id"]
        session._creation_data["race_name"] = race["name"]
        session._creation_data["starting_room"] = start_room
        session.starting_room_id = start_room
        session.race = race["name"]
        session.race_id = race["id"]
        session.state = "create_profession"
        await session.send_line(f"\r\n  Race: {race['name']}")
        await session.send_line(f"  Starts in: {start_town}")
        await self._show_profession_menu(session)

    # --- Step 4: Profession ---
    async def _show_profession_menu(self, session):
        professions = self._get_professions()
        prof_stats = self._get_profession_stats()
        primes = self._get_prime_requisites()
        await session.send_line("\r\nChoose your profession:\r\n")
        for i, prof in enumerate(professions, 1):
            stats = prof_stats.get(prof["id"], {"hp": 10, "mana": 0})
            prime = primes.get(prof["id"], (0, 1))
            prime_names = f"{STAT_ABBREVS[prime[0]]}/{STAT_ABBREVS[prime[1]]}"
            mana_str = f", Mana/lvl: {stats['mana']}" if stats["mana"] > 0 else ""
            await session.send_line(
                f"  {i:>2}. {prof['name']:<12} [{prof['type']:<6}] - {prof['desc']}"
            )
            await session.send_line(
                f"      HP/level: {stats['hp']}{mana_str}   Prime stats: {prime_names}"
            )
        await session.send(f"\r\nEnter choice (1-{len(professions)}): ")

    async def _step_profession(self, session, choice):
        professions = self._get_professions()
        try:
            idx = int(choice.strip())
            if idx < 1 or idx > len(professions):
                raise ValueError
        except ValueError:
            await session.send(f"Enter a number 1-{len(professions)}: ")
            return
        prof = professions[idx - 1]
        session._creation_data["profession_id"] = prof["id"]
        session._creation_data["profession_name"] = prof["name"]
        session.profession = prof["name"]
        session.profession_id = prof["id"]
        session.state = "create_culture"
        await session.send_line(f"\r\n  Profession: {prof['name']} ({prof['type']})")
        await self._show_culture_menu(session)

    # --- Step 5: Stat Allocation ---

    def _make_bar(self, value, width=20):
        """Visual bar [========------] scaled 0-100."""
        filled = round((value / 100) * width)
        filled = max(0, min(width, filled))
        return "[" + "=" * filled + "-" * (width - filled) + "]"

    def _init_stats(self, session):
        """Initialize stat array. Primes start at 30, others at 20."""
        prof_id = session._creation_data["profession_id"]
        primes = self._get_prime_requisites().get(prof_id, (0, 1))
        stats = [STAT_MIN] * NUM_STATS
        stats[primes[0]] = PRIME_MIN
        stats[primes[1]] = PRIME_MIN
        return stats

    async def _show_stat_allocation(self, session):
        race_id = session._creation_data["race_id"]
        prof_id = session._creation_data["profession_id"]
        prof_name = session._creation_data["profession_name"]
        mods = self._get_race_stat_mods().get(race_id, [0]*10)
        primes = self._get_prime_requisites().get(prof_id, (0, 1))

        if "stats" not in session._creation_data:
            session._creation_data["stats"] = self._init_stats(session)
            session._creation_data["selected_stat"] = None

        stats = session._creation_data["stats"]
        used = sum(stats)
        remaining = TOTAL_STAT_POINTS - used

        # Calculate TP preview
        # For TP calc we use the total (base + race mod) values
        total_stats = [stats[i] + mods[i] for i in range(NUM_STATS)]
        ptp, mtp = calc_tp(total_stats, prof_id)

        await session.send_line("")
        await session.send_line("=" * 74)
        await session.send_line(f"  STAT ALLOCATION      {prof_name} - {session._creation_data['race_name']}")
        await session.send_line(f"  Points: {used}/{TOTAL_STAT_POINTS} used, {remaining} remaining")
        await session.send_line(f"  Training Points/lvl:  Physical {ptp}   Mental {mtp}")
        await session.send_line("=" * 74)
        await session.send_line("")
        await session.send_line(
            f"  {'#':<3} {'Stat':<13}{'Base':>5} {'Race':>5} {'Total':>5} {'Bonus':>5}  {'':22}"
        )
        await session.send_line(
            f"  {'~'*3} {'~'*13}{'~'*5} {'~'*5} {'~'*5} {'~'*5}  {'~'*22}"
        )

        for i in range(NUM_STATS):
            mod = mods[i]
            total = stats[i] + mod
            bonus = stat_bonus(total)
            sign_mod = f"+{mod}" if mod >= 0 else str(mod)
            sign_bon = f"+{bonus}" if bonus >= 0 else str(bonus)
            bar = self._make_bar(total)
            prime_mark = " *" if i in primes else ""
            await session.send_line(
                f"  {i+1:<3} {STAT_NAMES[i]:<13}{stats[i]:>5} {sign_mod:>5} {total:>5} {sign_bon:>5}  {bar}{prime_mark}"
            )

        await session.send_line("")
        p1, p2 = STAT_NAMES[primes[0]], STAT_NAMES[primes[1]]
        await session.send_line(f"  * = Prime requisite ({p1}, {p2}) — starts at 30, +10 free")
        await session.send_line("")
        await session.send_line("  Commands:")
        await session.send_line("    <#>            Select a stat         (e.g. 3 to select Dexterity)")
        await session.send_line("    <#> <value>    Set a stat directly   (e.g. 3 92 for Dexterity=92)")
        await session.send_line("    + / -          Adjust selected by 5")
        await session.send_line("    SUGGEST        Auto-fill recommended build")
        await session.send_line("    RESET          Reset all stats to starting values")
        await session.send_line("    DONE           Accept and continue")

        sel = session._creation_data.get("selected_stat")
        if sel is not None:
            total = stats[sel] + mods[sel]
            bonus = stat_bonus(total)
            sign = f"+{bonus}" if bonus >= 0 else str(bonus)
            await session.send_line(f"\r\n  >> {STAT_NAMES[sel]}  base {stats[sel]}, total {total}, bonus {sign}")
            await session.send_line(f"     {STAT_DESCRIPTIONS[sel]}")

        await session.send("\r\n> ")

    async def _step_stats(self, session, raw_input):
        raw = raw_input.strip().lower()
        stats = session._creation_data["stats"]
        mods = self._get_race_stat_mods().get(session._creation_data["race_id"], [0]*10)
        prof_id = session._creation_data["profession_id"]
        primes = self._get_prime_requisites().get(prof_id, (0, 1))

        if raw == "reset":
            session._creation_data["stats"] = self._init_stats(session)
            session._creation_data["selected_stat"] = None
            await self._show_stat_allocation(session)
            return

        if raw == "suggest":
            suggested = self._get_suggested_stats(prof_id, primes)
            session._creation_data["stats"] = suggested
            session._creation_data["selected_stat"] = None
            await session.send_line("\r\n  Suggested build applied. Review and tweak as you like.")
            await self._show_stat_allocation(session)
            return

        if raw == "done":
            remaining = TOTAL_STAT_POINTS - sum(stats)
            if remaining > 0:
                await session.send_line(f"\r\n  You still have {remaining} points to spend!")
                await session.send_line("  Type SUGGEST for a recommended build, or allocate manually.")
                await session.send("> ")
                return
            session.state = "create_hair_color"
            await self._show_hair_color_menu(session)
            return

        if raw in ("+", "plus", "up"):
            sel = session._creation_data.get("selected_stat")
            if sel is None:
                await session.send_line("  Select a stat first (type 1-10).")
                await session.send("> ")
                return
            return await self._adjust_stat(session, sel, 5)

        if raw in ("-", "minus", "down"):
            sel = session._creation_data.get("selected_stat")
            if sel is None:
                await session.send_line("  Select a stat first (type 1-10).")
                await session.send("> ")
                return
            return await self._adjust_stat(session, sel, -5)

        parts = raw.split()

        # Two numbers: set stat directly  (e.g. "3 92")
        if len(parts) == 2:
            try:
                stat_idx = int(parts[0]) - 1
                new_val = int(parts[1])
                if stat_idx < 0 or stat_idx > 9:
                    raise ValueError
                min_val = PRIME_MIN if stat_idx in primes else STAT_MIN
                if new_val < min_val or new_val > STAT_MAX:
                    await session.send_line(f"  {STAT_NAMES[stat_idx]} range: {min_val}-{STAT_MAX}.")
                    await session.send("> ")
                    return
                return await self._set_stat(session, stat_idx, new_val)
            except (ValueError, IndexError):
                pass

        # Single number: could be stat selection OR a value for already-selected stat
        if len(parts) == 1:
            try:
                num = int(parts[0])

                # If 1-10 and no stat selected, or clearly a stat index: select it
                if 1 <= num <= 10:
                    sel = session._creation_data.get("selected_stat")
                    # If nothing selected, or if this looks like a stat number, select it
                    if sel is None or num <= 10:
                        idx = num - 1
                        session._creation_data["selected_stat"] = idx
                        total = stats[idx] + mods[idx]
                        bonus = stat_bonus(total)
                        sign = f"+{bonus}" if bonus >= 0 else str(bonus)
                        await session.send_line(f"\r\n  >> {STAT_NAMES[idx]}  base {stats[idx]}, total {total}, bonus {sign}")
                        await session.send_line(f"     {STAT_DESCRIPTIONS[idx]}")
                        p_mark = "  (Prime requisite)" if idx in primes else ""
                        await session.send_line(f"     Use + / - to adjust, or type a value ({PRIME_MIN if idx in primes else STAT_MIN}-{STAT_MAX}){p_mark}")
                        await session.send("> ")
                        return

                # If a stat IS selected and number is in valid stat range, set it
                sel = session._creation_data.get("selected_stat")
                if sel is not None:
                    min_val = PRIME_MIN if sel in primes else STAT_MIN
                    if min_val <= num <= STAT_MAX:
                        return await self._set_stat(session, sel, num)

            except ValueError:
                pass

        await session.send_line("  Type a stat # (1-10), '<#> <value>', +, -, SUGGEST, RESET, or DONE.")
        await session.send("> ")

    async def _set_stat(self, session, stat_idx, new_val):
        stats = session._creation_data["stats"]
        mods = self._get_race_stat_mods().get(session._creation_data["race_id"], [0]*10)
        prof_id = session._creation_data["profession_id"]
        primes = self._get_prime_requisites().get(prof_id, (0, 1))

        old_val = stats[stat_idx]
        diff = new_val - old_val
        remaining = TOTAL_STAT_POINTS - sum(stats)

        if diff > remaining:
            await session.send_line(f"  Not enough points! Need {diff}, have {remaining}.")
            await session.send("> ")
            return

        stats[stat_idx] = new_val
        session._creation_data["selected_stat"] = stat_idx
        new_remaining = TOTAL_STAT_POINTS - sum(stats)
        total = new_val + mods[stat_idx]
        bonus = stat_bonus(total)
        sign = f"+{bonus}" if bonus >= 0 else str(bonus)
        bar = self._make_bar(total)

        # Recalc TPs
        total_stats = [stats[i] + mods[i] for i in range(NUM_STATS)]
        ptp, mtp = calc_tp(total_stats, prof_id, primes)

        await session.send_line(f"  {STAT_NAMES[stat_idx]}: {old_val} -> {new_val}  total {total}  bonus {sign}  {bar}")
        await session.send_line(f"  Remaining: {new_remaining}   PTP: {ptp}  MTP: {mtp}")
        await session.send("> ")

    async def _adjust_stat(self, session, stat_idx, amount):
        stats = session._creation_data["stats"]
        primes = self._get_prime_requisites().get(session._creation_data["profession_id"], (0, 1))
        min_val = PRIME_MIN if stat_idx in primes else STAT_MIN

        new_val = stats[stat_idx] + amount
        new_val = max(min_val, min(STAT_MAX, new_val))
        await self._set_stat(session, stat_idx, new_val)

    def _get_suggested_stats(self, prof_id, primes):
        """Generate a sensible default stat spread that totals exactly 660."""
        # Priority-based allocation
        # Start everyone at minimums (primes at 30, rest at 20) = 200 + 20 = 220
        # Remaining: 660 - 220 = 440 to distribute
        stats = [STAT_MIN] * NUM_STATS
        stats[primes[0]] = PRIME_MIN
        stats[primes[1]] = PRIME_MIN

        # Profession-specific suggested allocations (all total 660)
        suggestions = {
            1:  [90, 85, 65, 65, 70, 40, 40, 55, 40, 70],  # Warrior
            2:  [60, 50, 92, 90, 68, 45, 50, 80, 40, 45],  # Rogue
            3:  [40, 50, 50, 60, 70, 95, 90, 55, 55, 55],  # Wizard
            4:  [50, 60, 50, 55, 60, 55, 55, 80, 92, 63],  # Cleric
            5:  [40, 60, 50, 55, 65, 55, 50, 60, 90, 95],  # Empath
            6:  [40, 50, 50, 55, 65, 95, 90, 55, 80, 40],  # Sorcerer
            7:  [65, 55, 90, 65, 65, 50, 45, 85, 55, 40],  # Ranger
            8:  [50, 50, 60, 60, 55, 70, 50, 60, 50, 95],  # Bard
            9:  [90, 80, 55, 60, 65, 50, 40, 50, 90, 40],  # Paladin
            10: [80, 65, 60, 90, 85, 50, 55, 60, 40, 35],  # Monk
        }
        return list(suggestions.get(prof_id, stats))

    # --- Appearance steps ---
    def _get_hair_colors(self, session):
        ap = _load_appearance_data(self.server)
        if ap and ap.get("hair_colors"):
            return ap["hair_colors"]
        return HAIR_COLORS

    def _get_hair_styles(self, session):
        ap = _load_appearance_data(self.server)
        if ap and ap.get("hair_styles"):
            return ap["hair_styles"]
        return HAIR_STYLES

    def _get_eye_colors(self, session):
        ap = _load_appearance_data(self.server)
        if ap and ap.get("eye_colors"):
            return ap["eye_colors"]
        return EYE_COLORS

    def _get_skin_tones(self, session):
        ap = _load_appearance_data(self.server)
        if ap and ap.get("skin_tones"):
            return ap["skin_tones"]
        return SKIN_TONES

    async def _show_hair_color_menu(self, session):
        colors = self._get_hair_colors(session)
        await session.send_line("\r\n  APPEARANCE - Hair Color\r\n")
        for i, color in enumerate(colors, 1):
            await session.send(f"  {i:>2}. {color:<22}")
            if i % 3 == 0:
                await session.send_line("")
        if len(colors) % 3 != 0:
            await session.send_line("")
        await session.send(f"\r\nChoose hair color (1-{len(colors)}): ")

    async def _step_hair_color(self, session, choice):
        colors = self._get_hair_colors(session)
        try:
            idx = int(choice.strip())
            if idx < 1 or idx > len(colors):
                raise ValueError
        except ValueError:
            await session.send(f"Enter 1-{len(colors)}: ")
            return
        session._creation_data["hair_color"] = colors[idx - 1]
        session.hair_color = colors[idx - 1]
        session.state = "create_hair_style"
        await self._show_hair_style_menu(session)

    async def _show_hair_style_menu(self, session):
        styles = self._get_hair_styles(session)
        await session.send_line("\r\n  APPEARANCE - Hair Style\r\n")
        for i, style in enumerate(styles, 1):
            await session.send(f"  {i:>2}. {style:<22}")
            if i % 3 == 0:
                await session.send_line("")
        if len(styles) % 3 != 0:
            await session.send_line("")
        await session.send(f"\r\nChoose hair style (1-{len(styles)}): ")

    async def _step_hair_style(self, session, choice):
        styles = self._get_hair_styles(session)
        try:
            idx = int(choice.strip())
            if idx < 1 or idx > len(styles):
                raise ValueError
        except ValueError:
            await session.send(f"Enter 1-{len(styles)}: ")
            return
        session._creation_data["hair_style"] = styles[idx - 1]
        session.hair_style = styles[idx - 1]
        session.state = "create_eye_color"
        await self._show_eye_color_menu(session)

    async def _show_eye_color_menu(self, session):
        colors = self._get_eye_colors(session)
        await session.send_line("\r\n  APPEARANCE - Eye Color\r\n")
        for i, color in enumerate(colors, 1):
            await session.send(f"  {i:>2}. {color:<22}")
            if i % 3 == 0:
                await session.send_line("")
        if len(colors) % 3 != 0:
            await session.send_line("")
        await session.send(f"\r\nChoose eye color (1-{len(colors)}): ")

    async def _step_eye_color(self, session, choice):
        colors = self._get_eye_colors(session)
        try:
            idx = int(choice.strip())
            if idx < 1 or idx > len(colors):
                raise ValueError
        except ValueError:
            await session.send(f"Enter 1-{len(colors)}: ")
            return
        session._creation_data["eye_color"] = colors[idx - 1]
        session.eye_color = colors[idx - 1]
        session.state = "create_skin_tone"
        await self._show_skin_menu(session)

    async def _show_skin_menu(self, session):
        tones = self._get_skin_tones(session)
        await session.send_line("\r\n  APPEARANCE - Skin Tone\r\n")
        for i, tone in enumerate(tones, 1):
            await session.send(f"  {i:>2}. {tone:<22}")
            if i % 3 == 0:
                await session.send_line("")
        if len(tones) % 3 != 0:
            await session.send_line("")
        await session.send(f"\r\nChoose skin tone (1-{len(tones)}): ")

    async def _step_skin_tone(self, session, choice):
        tones = self._get_skin_tones(session)
        try:
            idx = int(choice.strip())
            if idx < 1 or idx > len(tones):
                raise ValueError
        except ValueError:
            await session.send(f"Enter 1-{len(tones)}: ")
            return
        session._creation_data["skin_tone"] = tones[idx - 1]
        session.state = "create_height"
        await session.send_line("\r\n  APPEARANCE - Height")
        await session.send("Enter height in inches (48-84, avg ~68): ")

    async def _step_height(self, session, choice):
        try:
            h = int(choice.strip())
            if h < 48 or h > 84:
                raise ValueError
        except ValueError:
            await session.send("Enter a height between 48 and 84 inches: ")
            return
        session._creation_data["height"] = h
        session.height = h
        session.state = "create_age"
        await self._show_age_menu(session)

    # --- Step 5b: Culture ---

    def _get_culture_options(self, session):
        """
        Return (label, options_list) for the session's race.
        Data loaded from scripts/data/appearance.lua via LuaManager.
        Source: gswiki.play.net/Culture
        """
        race_id = session._creation_data.get("race_id", 1)
        appearance = _load_appearance_data(self.server)
        if appearance:
            cultures = appearance.get("cultures", {})
            block = cultures.get(race_id)
            if block and block.get("options"):
                return block["label"], block["options"]

        raise RuntimeError(
            "_get_culture_options: appearance.lua returned no culture data for race_id "
            f"{race_id}. Check scripts/data/appearance.lua."
        )
        return label, options

    async def _show_culture_menu(self, session):
        label, options = self._get_culture_options(session)
        race_name = session._creation_data.get("race_name", "")
        await session.send_line(f"\r\n  {label} — {race_name}\r\n")
        for i, opt in enumerate(options, 1):
            await session.send_line(f"  {i:>2}. {opt['name']}")
            await session.send_line(f"      {opt['desc']}")
        await session.send_line("")
        await session.send_line("  You may skip this choice now and set it later in-game")
        await session.send_line("  with TITLE SET CULTURE.  Type SKIP to leave unset.")
        await session.send(f"\r\nEnter choice (1-{len(options)}) or SKIP: ")

    async def _step_culture(self, session, choice):
        raw = choice.strip().lower()
        label, options = self._get_culture_options(session)

        if raw in ("skip", "s", "0", ""):
            session._creation_data["culture_key"]  = None
            session._creation_data["culture_name"] = "None (set later)"
            session.state = "create_stats"
            await self._show_stat_allocation(session)
            return

        try:
            idx = int(raw)
            if idx < 1 or idx > len(options):
                raise ValueError
        except ValueError:
            await session.send(f"Enter a number 1-{len(options)} or SKIP: ")
            return

        chosen = options[idx - 1]
        session._creation_data["culture_key"]  = chosen["key"]
        session._creation_data["culture_name"] = chosen["name"]
        await session.send_line(f"\r\n  Culture: {chosen['name']}")
        session.state = "create_stats"
        await self._show_stat_allocation(session)

    # --- Step 9b: Age ---

    def _get_age_ranges(self, session):
        """
        Return (stage_names, ranges_list) for the session's race from Lua,
        or a human-equivalent fallback.
        stage_names : list of 11 stage label strings
        ranges_list : list of 11 [min, max] pairs
        """
        race_id = session._creation_data.get("race_id", 1)
        appearance = _load_appearance_data(self.server)
        if appearance:
            age_ranges = appearance.get("age_ranges", {})
            stage_names = appearance.get("age_stage_names", [])
            ranges = age_ranges.get(race_id)
            if ranges and stage_names:
                return stage_names, ranges
        raise RuntimeError(
            "_get_age_ranges: appearance.lua returned no age data for race_id "
            f"{race_id}. Check scripts/data/appearance.lua."
        )
        return stage_names, ranges

    async def _show_age_menu(self, session):
        stage_names, ranges = self._get_age_ranges(session)
        race_name = session._creation_data.get("race_name", "")
        await session.send_line(f"\r\n  AGE — {race_name}\r\n")
        await session.send_line(f"  {'Stage':<22} {'Age Range':<16}")
        await session.send_line(f"  {'~'*22} {'~'*16}")
        for i, (stage, rng) in enumerate(zip(stage_names, ranges), 1):
            lo, hi = rng[0], rng[1]
            hi_str = str(hi) if hi < 999 else "+"
            await session.send_line(f"  {i:>2}. {stage:<20} {lo}-{hi_str}")
        await session.send_line("")
        await session.send_line("  Enter a stage number OR a specific numeric age.")
        await session.send_line("  Type SKIP to leave age unset (set later with AGE SET).")
        await session.send(f"\r\nEnter stage (1-{len(ranges)}), age, or SKIP: ")

    async def _step_age(self, session, choice):
        raw = choice.strip().lower()
        stage_names, ranges = self._get_age_ranges(session)

        if raw in ("skip", "s", ""):
            session._creation_data["age"] = None
            session.state = "create_confirm"
            await self._show_confirmation(session)
            return

        try:
            val = int(raw)
        except ValueError:
            await session.send(f"Enter a number, age, or SKIP: ")
            return

        # If 1-len(ranges): treat as stage selection, pick midpoint of range
        if 1 <= val <= len(ranges):
            lo, hi = ranges[val - 1]
            age = (lo + min(hi, lo + 20)) // 2  # midpoint, cap hi at lo+20 for open-ended
            session._creation_data["age"] = age
            await session.send_line(f"\r\n  Age: {age} ({stage_names[val - 1]})")
        else:
            # Treat as explicit age - validate it falls within any stage
            min_age = ranges[0][0]
            max_age = 9999
            if val < min_age:
                await session.send(f"Minimum age for your race is {min_age}: ")
                return
            session._creation_data["age"] = val
            # Find stage label for display
            stage_label = stage_names[-1]
            for stage, rng in zip(stage_names, ranges):
                if rng[0] <= val <= rng[1]:
                    stage_label = stage
                    break
            await session.send_line(f"\r\n  Age: {val} ({stage_label})")

        session.state = "create_confirm"
        await self._show_confirmation(session)

    # --- Confirmation ---
    async def _show_confirmation(self, session):
        d = session._creation_data
        race_mods = self._get_race_stat_mods().get(d["race_id"], [0]*10)
        stats = d["stats"]
        prof_stats = self._get_profession_stats().get(d["profession_id"], {"hp": 10, "mana": 0})
        primes = self._get_prime_requisites().get(d["profession_id"], (0, 1))
        start_room = int(d.get("starting_room") or self._get_default_starting_room())
        start_town = self._get_race_town_names().get(start_room, "Unknown")

        total_stats = [stats[i] + race_mods[i] for i in range(NUM_STATS)]
        ptp, mtp = calc_tp(total_stats, d["profession_id"], primes)

        feet = d["height"] // 12
        inches = d["height"] % 12

        await session.send_line("\r\n" + "=" * 55)
        await session.send_line("          CHARACTER SUMMARY")
        await session.send_line("=" * 55)
        await session.send_line(f"\r\n  Name:        {d['name']}")
        await session.send_line(f"  Gender:      {d['gender'].capitalize()}")
        await session.send_line(f"  Race:        {d['race_name']}")
        await session.send_line(f"  Culture:     {d.get('culture_name', 'None (set later)')}")
        await session.send_line(f"  Profession:  {d['profession_name']}")
        await session.send_line(f"  Height:      {feet}'{inches}\"")
        age_str = str(d['age']) if d.get('age') else 'Not set'
        await session.send_line(f"  Age:         {age_str}")
        await session.send_line(f"  Hair:        {d.get('hair_style','short')} {d.get('hair_color','brown')}")
        await session.send_line(f"  Eyes:        {d.get('eye_color','blue')}")
        await session.send_line(f"  Skin:        {d.get('skin_tone','fair')}")
        await session.send_line(f"  Starts in:   {start_town}")

        await session.send_line(f"\r\n  {'Stat':<13}{'Base':>5} {'Race':>5} {'Total':>5} {'Bonus':>5}  {'':22}")
        await session.send_line(f"  {'~'*13}{'~'*5} {'~'*5} {'~'*5} {'~'*5}  {'~'*22}")
        for i in range(NUM_STATS):
            mod = race_mods[i]
            total = stats[i] + mod
            bonus = stat_bonus(total)
            sign_mod = f"+{mod}" if mod >= 0 else str(mod)
            sign_bon = f"+{bonus}" if bonus >= 0 else str(bonus)
            bar = self._make_bar(total)
            prime_mark = " *" if i in primes else ""
            await session.send_line(
                f"  {STAT_NAMES[i]:<13}{stats[i]:>5} {sign_mod:>5} {total:>5} {sign_bon:>5}  {bar}{prime_mark}"
            )

        await session.send_line(f"\r\n  HP/level: {prof_stats['hp']}   Mana/level: {prof_stats['mana']}")
        await session.send_line(f"  Training Points/lvl:  Physical {ptp}   Mental {mtp}")
        await session.send_line("\r\n  Accept this character? (yes/no): ")

    async def _step_confirm(self, session, choice):
        if choice.strip().lower() in ("y", "yes"):
            await self._finalize_character(session)
        elif choice.strip().lower() in ("n", "no"):
            await session.send_line("Starting over...\r\n")
            await self.start(session)
        else:
            await session.send("Enter 'yes' or 'no': ")

    async def _finalize_character(self, session):
        d = session._creation_data
        race_mods = self._get_race_stat_mods().get(d["race_id"], [0]*10)
        stats = d["stats"]
        prof_stats = self._get_profession_stats().get(d["profession_id"], {"hp": 10, "mana": 0})
        primes = self._get_prime_requisites().get(d["profession_id"], (0, 1))
        start_room = int(d.get("starting_room") or self._get_default_starting_room())

        char_data = {
            "name": d["name"],
            "race_id": d["race_id"],
            "profession_id": d["profession_id"],
            "gender": d["gender"],
            "culture_key": d.get("culture_key"),
            "strength": stats[0] + race_mods[0],
            "constitution": stats[1] + race_mods[1],
            "dexterity": stats[2] + race_mods[2],
            "agility": stats[3] + race_mods[3],
            "discipline": stats[4] + race_mods[4],
            "aura": stats[5] + race_mods[5],
            "logic": stats[6] + race_mods[6],
            "intuition": stats[7] + race_mods[7],
            "wisdom": stats[8] + race_mods[8],
            "influence": stats[9] + race_mods[9],
            "health_max": 100 + prof_stats["hp"],
            "mana_max": prof_stats["mana"] * 3,
            "spirit_max": 10,
            "stamina_max": 100,
            "starting_room": start_room,
            "height": d.get("height", 70),
            "hair_color": d.get("hair_color", "brown"),
            "hair_style": d.get("hair_style", "short"),
            "eye_color": d.get("eye_color", "blue"),
            "skin_tone": d.get("skin_tone", "fair"),
            "age": d.get("age"),
        }

        char_id = None
        if self.server.db:
            char_id = self.server.db.create_character(session.account_id, char_data)
        session.character_id = char_id

        # Calculate and store starting TPs
        total_stats = [
            char_data["strength"], char_data["constitution"],
            char_data["dexterity"], char_data["agility"],
            char_data["discipline"], char_data["aura"],
            char_data["logic"], char_data["intuition"],
            char_data["wisdom"], char_data["influence"],
        ]
        ptp, mtp = calc_tp(total_stats, d["profession_id"], primes)
        session.physical_tp = ptp
        session.mental_tp   = mtp
        if char_id and self.server.db:
            self.server.db.save_character_tps(char_id, ptp, mtp)

        session.stat_strength = char_data["strength"]
        session.stat_constitution = char_data["constitution"]
        session.stat_dexterity = char_data["dexterity"]
        session.stat_agility = char_data["agility"]
        session.stat_discipline = char_data["discipline"]
        session.stat_aura = char_data["aura"]
        session.stat_logic = char_data["logic"]
        session.stat_intuition = char_data["intuition"]
        session.stat_wisdom = char_data["wisdom"]
        session.stat_influence = char_data["influence"]
        session.health_max = char_data["health_max"]
        session.health_current = char_data["health_max"]
        session.mana_max = char_data["mana_max"]
        session.mana_current = char_data["mana_max"]

        # ============================================================
        # STARTER GEAR - Give new character their starting equipment
        # ============================================================
        if char_id and self.server.db:
            prof_id = d["profession_id"]

            # ── Starter gear is defined exclusively in scripts/data/starter_gear.lua ──
            lua_gear    = _require_lua_data(self.server, "get_starter_gear")
            gear_config = lua_gear.get("kits", {}).get(prof_id)
            starting_silver = lua_gear.get("starting_silver", {}).get(prof_id, 500)
            log.info("starter_gear: loaded Lua kit for prof %d (%s)",
                     prof_id, gear_config.get("description", "?") if gear_config else "none")

            # Starting silver
            session.silver = starting_silver
            self.server.db.save_character_resources(
                char_id,
                char_data["health_max"], char_data["mana_max"],
                10, 100, starting_silver
            )

            # Add items to inventory
            # Add items to inventory with proper slots
            if gear_config:
                container_inv_ids = {}
                for item_entry in gear_config.get("items", []):
                    item_id = item_entry.get("item_id")
                    if not item_id:
                        continue

                    slot = item_entry.get("slot")
                    container_noun = item_entry.get("container")
                    hand = item_entry.get("hand")

                    if hand:
                        hand_slot = "right_hand" if hand == "right" else "left_hand"
                        inv_id = self.server.db.add_item_to_inventory(char_id, item_id, slot=hand_slot)
                    elif slot:
                        inv_id = self.server.db.add_item_to_inventory(char_id, item_id, slot=slot)
                        noun = item_entry.get("name", "").split()[-1]
                        container_inv_ids[noun] = inv_id
                    elif container_noun and container_noun in container_inv_ids:
                        inv_id = self.server.db.add_item_to_inventory(char_id, item_id)
                        if inv_id:
                            try:
                                conn = self.server.db._get_conn()
                                cur = conn.cursor()
                                cur.execute("UPDATE character_inventory SET container_id = %s WHERE id = %s",
                                            (container_inv_ids[container_noun], inv_id))
                                conn.close()
                            except Exception as e:
                                log.error("Failed to set container: %s", e)
                    else:
                        self.server.db.add_item_to_inventory(char_id, item_id)

                # Load inventory with hand restoration
                restore_inventory_state(self.server, session)

                log.info("Gave starter gear to %s (prof %s): %d items, %d silver",
                         d["name"], d["profession_name"],
                         len(gear_config.get("items", [])), session.silver)


        await session.send_line(f"\r\n{'='*55}")
        await session.send_line(f"  {d['name']} the {d['race_name']} {d['profession_name']} enters the world...")
        await session.send_line(f"{'='*55}\r\n")

        if hasattr(self.server, 'tutorial'):
            await self.server.tutorial.start_tutorial(session)
        else:
            session.state = "playing"
            room = self.server.world.get_room(start_room)
            if not room:
                log.warning("finalize_character: start_room %d not loaded, falling back to 221", start_room)
                room = self.server.world.get_room(221)
            if room:
                session.current_room = room
                self.server.world.add_player_to_room(session, room.id)
                await self.server.commands.handle(session, "look")
            else:
                await session.send("(Warning: starting room not found!)\r\n>")
