"""
ExperienceManager - GemStone IV experience system.

All XP from any source goes into field_experience pool first.
Absorbed into total experience over time via absorb_tick().

Mind state warnings:
  - Every kill shows current mind state
  - At "saturated" (85%+) and "you must rest!" (95%+), every kill warns you
  - Auto-notifies when mind returns to "clear as a bell" from any filled state
"""

import logging
from server.core.protocol.colors import (
    colorize, TextPresets, experience_msg, level_up_msg
)
from server.core.commands.player.info import award_fame

log = logging.getLogger(__name__)

MIND_STATES = [
    (0.00, "clear as a bell"),
    (0.12, "clear"),
    (0.25, "fresh and clear"),
    (0.40, "fresh"),
    (0.55, "muddled"),
    (0.70, "becoming saturated"),
    (0.85, "saturated"),
    (0.95, "you must rest!"),
    (1.00, "fried"),
]

# GS4 canon base rates in XP-per-MINUTE.
# absorb_tick() fires every 5s (12 ticks/min), so divide by 12 per tick.
_ABSORB_PER_MIN_SUPERNODE = 27
_ABSORB_PER_MIN_NODE      = 25
_ABSORB_PER_MIN_TOWN      = 23
_ABSORB_PER_MIN_OUTDOORS  = 16

# Single-player absorption speed multiplier.
# x1 = vanilla GS4 (~7min full clear in town).
# x3 = comfortable solo pace (~2.5min).
# x8 = fast solo grind (~1min). Tune to taste.
SP_ABSORB_MULTIPLIER = 3

# Flat multiplier applied to ALL XP gains from every source (kills, lockpicking,
# crafting, bounties, etc.).
# x1 = vanilla GS4.  x3 = current server gain rate.
XP_GAIN_MULTIPLIER = 3

# Field experience pool size multiplier.
# This is intentionally separate from XP_GAIN_MULTIPLIER so we can make the
# mind pool much larger without also inflating every XP award source.
XP_POOL_CAP_MULTIPLIER = 10

# Multiplier applied to the amount of XP drained from the pool each tick.
# Current solo server target is x18 total absorption throughput:
# SP_ABSORB_MULTIPLIER (x3) * XP_ABSORB_AMOUNT_MULTIPLIER (x6).
XP_ABSORB_AMOUNT_MULTIPLIER = 6

_FAME_SOURCE_DIVISORS = {
    "kill": 12,
    "quest": 12,
    "lockpicking": 16,
    "bounty": 12,
    "task": 12,
    "guild_task": 14,
    "crafting": 20,
}


def _fame_for_xp_gain(xp_amount: int, source: str) -> int:
    divisor = _FAME_SOURCE_DIVISORS.get((source or "").strip().lower())
    if not divisor or xp_amount <= 0:
        return 0
    return max(1, int(xp_amount / divisor))


def _get_absorb_rate(session):
    """Returns XP to absorb this tick (every 5 seconds).
    Sleeping gives a 2x bonus on top of the base rate.
    """
    room        = session.current_room
    logic_bonus = max(0, (getattr(session, 'stat_logic', 50) - 50) // 10)
    if room is None:
        base_per_min = _ABSORB_PER_MIN_OUTDOORS
    elif getattr(room, 'supernode', False):
        base_per_min = _ABSORB_PER_MIN_SUPERNODE
    elif getattr(room, 'safe', False):
        base_per_min = _ABSORB_PER_MIN_NODE
    elif getattr(room, 'indoor', False):
        base_per_min = _ABSORB_PER_MIN_TOWN
    else:
        base_per_min = _ABSORB_PER_MIN_OUTDOORS

    # Sleeping doubles absorption speed
    sleep_mult = 2 if getattr(session, 'position', 'standing') == 'sleeping' else 1

    # Convert per-minute rate to per-5-second tick, then apply multipliers
    per_tick = max(1, round((base_per_min * SP_ABSORB_MULTIPLIER * sleep_mult) / 12))
    return (per_tick + logic_bonus) * XP_ABSORB_AMOUNT_MULTIPLIER


def field_xp_capacity(session):
    logic_bonus = max(0, (getattr(session, 'stat_logic', 50) - 50) // 2)
    disc_bonus  = max(0, (getattr(session, 'stat_discipline', 50) - 50) // 2)
    return (800 * XP_POOL_CAP_MULTIPLIER) + logic_bonus + disc_bonus


def get_mind_fill_pct(session):
    capacity = field_xp_capacity(session)
    if capacity <= 0:
        return 0.0
    return min(1.0, getattr(session, 'field_experience', 0) / capacity)


def get_mind_state(session):
    pct   = get_mind_fill_pct(session)
    state = "clear as a bell"
    for threshold, name in MIND_STATES:
        if pct >= threshold:
            state = name
    return state


def absorption_bar(session):
    """Visual absorption bar for EXP command."""
    pct    = get_mind_fill_pct(session)
    filled = int(pct * 20)
    bar    = "[" + "#" * filled + "." * (20 - filled) + "]"
    mind   = get_mind_state(session)
    cap    = field_xp_capacity(session)
    cur    = getattr(session, 'field_experience', 0)
    if pct >= 0.85:
        color = TextPresets.COMBAT_DAMAGE_TAKEN
    elif pct >= 0.55:
        color = TextPresets.WARNING
    else:
        color = TextPresets.EXPERIENCE
    return colorize(f"  {bar} {cur}/{cap}  Mind: {mind}", color)


class ExperienceManager:

    def __init__(self, server):
        self.server       = server
        self._level_table = {}
        self._level_tp    = {}

    async def initialize(self):
        self._load_level_table()

    def _load_level_table(self):
        if not self.server.db:
            self._build_fallback_table()
            return
        try:
            rows = self.server.db.execute_query(
                "SELECT level, xp_required, tp_physical, tp_mental FROM levels ORDER BY level"
            )
            if not rows:
                self._build_fallback_table()
                return
            for row in rows:
                lvl, xp_req, tp_p, tp_m = row
                self._level_table[int(lvl)] = int(xp_req)
                self._level_tp[int(lvl)]    = (int(tp_p), int(tp_m))
        except Exception as e:
            log.warning("Could not load levels from DB (%s), using fallback", e)
            self._build_fallback_table()

    def _build_fallback_table(self):
        xp    = 0
        costs = (
            [(i, 10000) for i in range(1,  16)] +
            [(i,  8000) for i in range(16, 26)] +
            [(i,  6000) for i in range(26, 41)] +
            [(i,  4000) for i in range(41, 51)] +
            [(i,  2000) for i in range(51, 101)]
        )
        for lvl, cost in costs:
            self._level_table[lvl] = xp
            self._level_tp[lvl]    = (35 + lvl // 5, 35 + lvl // 5)
            xp += cost

    def xp_for_level(self, level):
        return self._level_table.get(level, level * 5000)

    # ── Core: award XP to pool — all sources use this ─────────────────────────

    async def award_xp_to_pool(self, session, xp_amount, source="", fame_detail_text=None):
        """
        Award XP into the field_experience pool.
        Used by kills, lockpicking, crafting, bounties — everything.
        Shows gain + mind state. Warns loudly at high fill states.
        Applies the Sunday bonus XP event multiplier if active.
        """
        if xp_amount <= 0:
            return 0

        xp_amount = xp_amount * XP_GAIN_MULTIPLIER

        # ── Sunday Bonus XP event multiplier ──────────────────────────────────
        event_mult = 1.0
        if hasattr(self.server, 'events'):
            event_mult = self.server.events.get_bonus_xp_multiplier()
        if event_mult > 1.0:
            xp_amount = int(xp_amount * event_mult)

        capacity = field_xp_capacity(session)
        current  = getattr(session, 'field_experience', 0)
        space    = max(0, capacity - current)

        if space <= 0:
            await session.send_line(colorize(
                "  Your mind is too full to absorb any more experience.  You must rest!",
                TextPresets.WARNING
            ))
            return 0

        xp_to_add = min(xp_amount, space)
        session.field_experience = current + xp_to_add

        mind    = get_mind_state(session)
        pct     = get_mind_fill_pct(session)
        # Show event bonus in source tag if active
        if event_mult > 1.0:
            src_str = f" [{source} x{event_mult:.0f}]" if source else f" [x{event_mult:.0f} event]"
        else:
            src_str = f" [{source}]" if source else ""

        # Choose color and warning based on mind state
        if pct >= 0.95:
            color = TextPresets.WARNING
            await session.send_line(colorize(
                f"  You gained {xp_to_add} experience{src_str}.  Mind: {mind}  -- You must rest!",
                color
            ))
        elif pct >= 0.85:
            color = TextPresets.WARNING
            await session.send_line(colorize(
                f"  You gained {xp_to_add} experience{src_str}.  Mind: {mind}  -- Consider resting soon.",
                color
            ))
        elif pct >= 0.70:
            color = TextPresets.EXPERIENCE
            await session.send_line(colorize(
                f"  You gained {xp_to_add} experience{src_str}.  Mind: {mind}",
                color
            ))
        else:
            await session.send_line(colorize(
                f"  You gained {xp_to_add} experience{src_str}.  Mind: {mind}",
                TextPresets.EXPERIENCE
            ))

        fame = _fame_for_xp_gain(xp_to_add, source)
        if fame:
            try:
                detail = fame_detail_text or (
                    f"Earned experience from {source}."
                    if source else
                    "Earned experience."
                )
                await award_fame(session, self.server, fame, source or "experience", detail_text=detail, quiet=True)
            except Exception:
                log.exception("Failed awarding fame from XP source '%s'", source)

        if self.server.db and session.character_id:
            self.server.db.save_character_experience(
                session.character_id, session.level,
                session.experience, session.field_experience
            )

        return xp_to_add

    # ── Kill XP ───────────────────────────────────────────────────────────────

    def calculate_kill_xp(self, session, creature):
        level_diff = creature.level - session.level
        if level_diff <= -10:
            xp = 0
        elif level_diff < 0:
            xp = max(5, 100 - (8 * abs(level_diff)))
        elif level_diff == 0:
            xp = 100
        elif level_diff <= 4:
            xp = min(200, 100 + (15 * level_diff))
        else:
            xp = min(300, 150 + (10 * (level_diff - 4)))

        # Diminishing returns as pool fills
        pct = get_mind_fill_pct(session)
        if pct >= 1.0:
            return 0
        elif pct >= 0.95:
            xp = int(xp * 0.10)
        elif pct >= 0.85:
            xp = int(xp * 0.30)
        elif pct >= 0.70:
            xp = int(xp * 0.60)
        elif pct >= 0.55:
            xp = int(xp * 0.80)
        return max(0, xp)

    async def award_kill_xp(self, session, creature):
        """Called on creature death. XP goes straight into the pool."""
        try:
            guild_engine = getattr(self.server, "guild", None)
            if guild_engine:
                await guild_engine.record_bounty_kill(session, creature)
        except Exception:
            log.exception("Failed to record bounty kill progress")

        xp = self.calculate_kill_xp(session, creature)
        if xp <= 0:
            if get_mind_fill_pct(session) >= 1.0:
                await session.send_line(colorize(
                    "  Your mind is completely fried.  You must rest before you can learn anything more!",
                    TextPresets.WARNING
                ))
            return
        await self.award_xp_to_pool(
            session,
            xp,
            source="kill",
            fame_detail_text=f"Defeated {getattr(creature, 'full_name', getattr(creature, 'name', 'a creature'))}.",
        )

    def calculate_lockpick_xp(self, session, lock_difficulty: int, endroll: int) -> int:
        """
        GS4 wiki: Picking locks awards XP scaled by lock difficulty.
        Harder locks relative to your skill = more XP.
        A trivial lock (well under your skill) gives very little.
        A challenging lock (near your limit) gives full value.
        An open-roll success on a tough lock gives bonus XP.

        Base XP = lock_difficulty * 1.5  (rough GS4 equivalent)
        Skill gap modifier:
          endroll 100-120  (barely made it)   -> x1.0  (full XP)
          endroll 121-150  (comfortable)      -> x0.8
          endroll 151-200  (easy)             -> x0.5
          endroll 200+     (trivial)          -> x0.25
        Min 5 XP, cap 500 pre-multiplier.
        """
        base = min(500, int(lock_difficulty * 1.5))

        if endroll <= 120:
            scale = 1.0
        elif endroll <= 150:
            scale = 0.8
        elif endroll <= 200:
            scale = 0.5
        else:
            scale = 0.25

        xp = max(5, int(base * scale))

        # Diminishing returns as pool fills (same as kill XP)
        pct = get_mind_fill_pct(session)
        if pct >= 1.0:   return 0
        elif pct >= 0.95: xp = int(xp * 0.10)
        elif pct >= 0.85: xp = int(xp * 0.30)
        elif pct >= 0.70: xp = int(xp * 0.60)
        elif pct >= 0.55: xp = int(xp * 0.80)

        return max(0, xp)

    async def award_lockpick_xp(self, session, lock_difficulty: int, endroll: int):
        """Award XP for successfully picking a lock. Multiplier already applied inside award_xp_to_pool."""
        xp = self.calculate_lockpick_xp(session, lock_difficulty, endroll)
        if xp > 0:
            await self.award_xp_to_pool(session, xp, source="lockpicking")

    async def collect_loot_xp(self, session, creature):
        pass

    async def award_decay_xp(self, session, creature):
        pass

    # ── Absorption pulse ──────────────────────────────────────────────────────

    # Messages shown when the mind state crosses a threshold while absorbing.
    # Keyed by the NEW state the player just entered.
    _MIND_TRANSITION_MSGS = {
        "clear as a bell":     ("Your mind feels completely clear.  You are ready to hunt again!",            TextPresets.EXPERIENCE),
        "clear":               ("Your thoughts begin to clear.  Your mind is becoming clear.",                TextPresets.EXPERIENCE),
        "fresh and clear":     ("The mental fog starts to lift.  Your mind is fresh and clear.",              TextPresets.EXPERIENCE),
        "fresh":               ("You feel mentally refreshed.  Your mind is fresh.",                          TextPresets.EXPERIENCE),
        "muddled":             ("Your thoughts grow a little sluggish.  Your mind feels muddled.",            TextPresets.WARNING),
        "becoming saturated":  ("Your mind is struggling to keep up.  It is becoming saturated.",             TextPresets.WARNING),
        "saturated":           ("Your mind is saturated with experience.  Consider resting soon.",            TextPresets.WARNING),
        "you must rest!":      ("Your mind is dangerously full.  You must rest before you lose focus!",       TextPresets.WARNING),
        "fried":               ("Your mind is completely fried.  You cannot learn anything more right now!",  TextPresets.WARNING),
    }

    async def absorb_tick(self, session):
        """
        Drain field_experience into experience. Called every 5s from game loop.
        Applies Gift of Lumnis absorption multiplier if active for this character.
        Notifies player on every mind state transition (threshold crossing only,
        never spams the same state repeatedly).
        """
        field = getattr(session, 'field_experience', 0)
        if field <= 0:
            return False

        prev_mind = get_mind_state(session)

        # Base amount to drain from the field pool this tick
        base_absorb = min(_get_absorb_rate(session), field)

        # ── Gift of Lumnis multiplier ─────────────────────────────────────────
        # The field pool drains at the BASE rate — Lumnis just gives more credit
        # per drained point. bonus_absorbed = extra XP added on top.
        lumnis_mult = 1.0
        if hasattr(self.server, 'events'):
            lumnis_mult = self.server.events.get_lumnis_absorption_multiplier(session)

        total_absorbed   = int(base_absorb * lumnis_mult)
        bonus_absorbed   = total_absorbed - base_absorb   # the Lumnis bonus portion

        session.field_experience -= base_absorb            # drain field at BASE rate
        session.experience       += total_absorbed         # credit at boosted rate

        # Report bonus to event manager so it can track phase exhaustion
        if bonus_absorbed > 0 and hasattr(self.server, 'events'):
            await self.server.events.on_lumnis_absorbed(session, bonus_absorbed)

        # Notify only when the state actually changes
        new_mind = get_mind_state(session)
        if new_mind != prev_mind:
            msg, color = self._MIND_TRANSITION_MSGS.get(
                new_mind,
                (f"Your mind is now: {new_mind}.", TextPresets.EXPERIENCE)
            )
            await session.send_line(colorize(f"  {msg}", color))

        # Check level up
        next_level = session.level + 1
        needed     = self.xp_for_level(next_level)
        if needed > 0 and session.experience >= needed and next_level <= 100:
            await self._level_up(session)
            return True

        return False

    async def absorb_all_players(self):
        for session in self.server.sessions.playing():
            try:
                await self.absorb_tick(session)
                if self.server.db and session.character_id:
                    self.server.db.save_character_experience(
                        session.character_id, session.level,
                        session.experience, session.field_experience
                    )
            except Exception as e:
                log.error("XP absorb error for %s: %s", session.character_name, e)

    # ── Level up ──────────────────────────────────────────────────────────────

    async def _level_up(self, session):
        session.level += 1
        new_level = session.level

        old_hp   = session.health_max
        old_mana = session.mana_max

        con_bonus = max(0, (getattr(session, 'stat_constitution', 50) - 50) // 5)
        hp_gain   = 10 + con_bonus
        session.health_max     += hp_gain
        session.health_current  = session.health_max

        aur_bonus = max(0, (getattr(session, 'stat_aura', 50) - 50) // 10)
        mana_gain = 3 + aur_bonus
        session.mana_max     += mana_gain
        session.mana_current  = session.mana_max

        session.stamina_max     += 5
        session.stamina_current  = session.stamina_max

        if new_level % 3 == 0:
            session.spirit_max     += 1
            session.spirit_current  = session.spirit_max

        tp_p, tp_m = self._level_tp.get(new_level, (35, 35))
        session.physical_tp += tp_p
        session.mental_tp   += tp_m

        # ── Refund overcharges from the level we just completed ───────────────
        # Any rank that was in the old level's "premium slots" (slot_pos > 1)
        # is now a prior-level rank and should have cost flat base.
        # Refund: base x (slot_pos - 1) per such rank actually held.
        # Example: TWC limit=2 base=2/2, old level had ranks 39(slot1) and 40(slot2).
        #   Rank 40 cost 4/4 but is now prior-level -> refund 2/2.
        from server.core.commands.player.training import (
            SKILL_COSTS, get_train_limit
        )
        old_level   = new_level - 1
        refund_ptp  = 0
        refund_mtp  = 0
        prof_id     = getattr(session, 'profession_id', 1)
        if session.skills:
            for skill_id, skill_data in session.skills.items():
                if not isinstance(skill_data, dict):
                    continue
                ranks = int(skill_data.get('ranks', 0))
                if ranks == 0:
                    continue
                ptp_base, mtp_base = SKILL_COSTS.get(skill_id, {}).get(prof_id, (0, 0))
                if ptp_base == 0 and mtp_base == 0:
                    continue
                limit = get_train_limit(skill_id, prof_id)
                if limit <= 0:
                    continue
                old_prev_cap = limit * (old_level - 1)
                # Slots 1..limit of the old level: ranks old_prev_cap+1 .. old_prev_cap+limit
                for rank in range(old_prev_cap + 1, old_prev_cap + limit + 1):
                    if rank > ranks:
                        break
                    slot_pos   = min(rank - old_prev_cap, 2)  # matches cost formula cap
                    overcharge = slot_pos - 1                  # 0 for slot 1, 1 for slot 2+
                    refund_ptp += ptp_base * overcharge
                    refund_mtp += mtp_base * overcharge
        if refund_ptp > 0 or refund_mtp > 0:
            session.physical_tp += refund_ptp
            session.mental_tp   += refund_mtp

        # ranks_this_level no longer used — cap is total = limit x level

        xp_next  = self.xp_for_level(new_level + 1)
        xp_this  = self.xp_for_level(new_level)
        xp_delta = xp_next - xp_this if xp_next > xp_this else 0

        await session.send_line("")
        await session.send_line(level_up_msg(new_level))
        await session.send_line(colorize(
            f"  Health: {old_hp} -> {session.health_max}  (+{hp_gain})",
            TextPresets.EXPERIENCE
        ))
        if mana_gain > 0:
            await session.send_line(colorize(
                f"  Mana:   {old_mana} -> {session.mana_max}  (+{mana_gain})",
                TextPresets.EXPERIENCE
            ))
        await session.send_line(colorize(
            f"  Training Points: +{tp_p} physical, +{tp_m} mental",
            TextPresets.EXPERIENCE
        ))
        if refund_ptp > 0 or refund_mtp > 0:
            await session.send_line(colorize(
                f"  Training Refund:  +{refund_ptp} physical, +{refund_mtp} mental"
                f"  (premium cost refund from last level's skill slots)",
                TextPresets.EXPERIENCE
            ))
        if xp_delta > 0:
            await session.send_line(colorize(
                f"  Next level requires {xp_delta:,} more experience.",
                TextPresets.SYSTEM
            ))
        await session.send_line("")

        if session.current_room:
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                colorize(
                    f"  {session.character_name} appears to have gained a new level!",
                    TextPresets.LEVEL_UP
                ),
                exclude=session
            )

        if self.server.db and session.character_id:
            self.server.db.save_character_experience(
                session.character_id, session.level,
                session.experience, session.field_experience
            )
            # Bug fix: TPs were not being persisted on level-up.
            # save_character() was missing physical_tp/mental_tp (now fixed),
            # but we also save immediately here so a crash/disconnect mid-session
            # cannot cause the awarded TPs to be lost.
            self.server.db.save_character_tps(
                session.character_id,
                session.physical_tp,
                session.mental_tp
            )

    # ── Convenience ───────────────────────────────────────────────────────────

    def get_mind_state_for_session(self, session):
        return get_mind_state(session)

    def get_xp_progress(self, session):
        this_xp  = self.xp_for_level(session.level)
        next_xp  = self.xp_for_level(session.level + 1)
        if next_xp <= this_xp:
            return session.experience, 0, 100.0
        progress = session.experience - this_xp
        needed   = next_xp - this_xp
        pct      = min(100.0, progress / needed * 100)
        return session.experience, needed, pct
