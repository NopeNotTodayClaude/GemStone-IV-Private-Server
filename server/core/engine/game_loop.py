"""
GameLoop - Main server tick loop.
Handles periodic updates: creature AI, NPC behavior, exp absorption, weather, spawns.
No auto-save here - saves happen in real-time via event handlers.
"""

import asyncio
import logging
import time

log = logging.getLogger(__name__)


class GameLoop:
    """Runs periodic server updates on a fixed tick rate."""

    def __init__(self, server):
        self.server = server
        self.tick_rate = server.config.get("server.tick_rate", 10)
        self.tick_interval = 1.0 / self.tick_rate
        self.tick_count = 0
        self._last_weather = time.time()
        self._last_xp_absorb = time.time()
        self._last_ground_cleanup = time.time()

    async def run(self):
        """Main loop - runs until server.running is False."""
        log.info("Game loop started (tick rate: %d/sec)", self.tick_rate)

        while self.server.running:
            tick_start = time.time()
            self.tick_count += 1

            try:
                await self._tick()
            except Exception as e:
                log.error("Game loop tick error: %s", e, exc_info=True)

            # Sleep for remainder of tick interval
            elapsed = time.time() - tick_start
            sleep_time = max(0, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

        log.info("Game loop stopped after %d ticks.", self.tick_count)

    async def _tick(self):
        """Single game tick."""
        now = time.time()

        # Scheduled world events (Lumnis, bonus XP) — checked every ~60s
        if hasattr(self.server, 'events'):
            try:
                await self.server.events.tick(now)
            except Exception as e:
                log.error("Event manager tick error: %s", e, exc_info=True)

        # Weather state machine — ticks every ~5 min per zone
        if hasattr(self.server, 'weather'):
            try:
                await self.server.weather.tick(now)
            except Exception as e:
                log.error("Weather tick error: %s", e, exc_info=True)

        # Creature AI tick (delegated to creature manager)
        if hasattr(self.server, 'creatures'):
            try:
                await self.server.creatures.tick(self.tick_count)
            except Exception as e:
                log.error("Creature tick error: %s", e, exc_info=True)

        # NPC tick (ambient emotes, patrol movement)
        if hasattr(self.server, 'npcs'):
            try:
                await self.server.npcs.tick(self.tick_count)
            except Exception as e:
                log.error("NPC tick error: %s", e, exc_info=True)

        # Experience absorption pulse (every 5 seconds)
        if now - self._last_xp_absorb >= 5.0:
            self._last_xp_absorb = now
            if hasattr(self.server, 'experience'):
                try:
                    await self.server.experience.absorb_all_players()
                except Exception as e:
                    log.error("XP absorption error: %s", e, exc_info=True)

            # Stat penalty recovery pulse (same 5s cadence as XP absorb)
            if hasattr(self.server, 'death'):
                try:
                    for session in self.server.sessions.playing():
                        mult = getattr(session, 'death_stat_mult', 1.0)
                        if mult < 1.0:
                            await self.server.death.stat_penalty_tick(session)
                except Exception as e:
                    log.error("Stat penalty recovery error: %s", e, exc_info=True)

        # Real-time sync push (every 10 ticks = ~1 second per player)
        if self.tick_count % 10 == 0:
            if hasattr(self.server, 'sync_broadcaster'):
                try:
                    await self.server.sync_broadcaster.broadcast_all()
                except Exception as e:
                    log.debug("Sync broadcast error: %s", e)

        # Status effects tick (bleed, poison, stun, flee, etc.)
        # server.status is the canonical StatusManager; fall back to shim if missing
        _status_engine = getattr(self.server, 'status', None) or getattr(self.server, 'status_effects', None)
        if _status_engine:
            try:
                await _status_engine.tick(self.tick_count)
            except Exception as e:
                log.error("Status effects tick error: %s", e, exc_info=True)

        # Passive health/mana/stamina regeneration (every ~60 seconds, matching GS4 regen cadence)
        if self.tick_count % 600 == 0:
            try:
                await self._regen_tick()
            except Exception as e:
                log.error("Regen tick error: %s", e, exc_info=True)

        if now - self._last_ground_cleanup >= 60.0:
            self._last_ground_cleanup = now
            try:
                if hasattr(self.server, "world"):
                    self.server.world.cleanup_ground_items()
            except Exception as e:
                log.error("Ground item cleanup error: %s", e, exc_info=True)

        # TODO: Weather changes, ambient messages

    async def _regen_tick(self):
        """
        Passive regeneration pulse (~every 60 seconds, matching GS4's per-round cadence).

        GS4 formula:
          Health  : Base(1) + trunc(CON_bonus / 2)  — matches HEALTH display
                    x1.5 if sitting/kneeling, x2.0 if lying
                    x1.5 bonus on a supernode
                    No regen during combat or while bleeding heavily
          Mana    : Base(1) + Spirit/Intuition bonus
                    x2.0 on a node/supernode
          Stamina : Base(2) + Constitution bonus / 4
                    x1.5 if sitting/lying
        """
        sessions = list(self.server.world.get_all_players())
        for session in sessions:
            if not session.connected or session.state != "playing":
                continue

            room = session.current_room
            supernode = getattr(room, 'supernode', False) if room else False
            is_node   = supernode or (getattr(room, 'safe', False) if room else False)
            position  = getattr(session, 'position', 'standing')
            in_combat = getattr(session, 'in_combat', False)

            # ── Health regen ──────────────────────────────────────────────────
            if session.health_current < session.health_max:
                # No regen while in combat, dead, poisoned, or bleeding (any amount).
                # Dead check: health <= 0 or status_manager "dead" effect.
                sm = getattr(self.server, 'status', None)
                if sm:
                    is_dead     = (session.health_current <= 0 or sm.has(session, 'dead'))
                    is_poisoned = (sm.has(session, 'poisoned') or sm.has(session, 'major_poison'))
                    is_diseased = sm.has(session, 'disease')
                    b_se        = sm.get_effect(session, 'major_bleed') or sm.get_effect(session, 'bleeding')
                    is_bleeding = b_se is not None
                    bleed_stacks = b_se.stacks if b_se else 0
                else:
                    # Fallback: read StatusEffect objects directly
                    effects      = getattr(session, 'status_effects', {}) or {}
                    b_effect     = effects.get('major_bleed') or effects.get('bleeding')
                    p_effect     = effects.get('major_poison') or effects.get('poisoned')
                    is_dead      = session.health_current <= 0
                    is_bleeding  = b_effect is not None and getattr(b_effect, 'active', True)
                    is_poisoned  = p_effect is not None and getattr(p_effect, 'active', True)
                    is_diseased  = False
                    bleed_stacks = getattr(b_effect, 'stacks', 0) if is_bleeding else 0

                # Suppress regen entirely: combat / dead / poisoned / major bleed (3+ stacks)
                suppress_regen = in_combat or is_dead or is_poisoned or is_diseased or bleed_stacks >= 3

                if not suppress_regen:
                    # HP regen formula — identical to what HEALTH command displays,
                    # multiplied x4 per server config.
                    con_bonus     = (getattr(session, 'stat_constitution', 50) - 50) // 2
                    base_hp_regen = max(1, con_bonus // 2 + 1) * 4

                    # Position multiplier
                    # 'sleeping' treated same as 'lying' — sleep DOES speed HP regen
                    if position in ('lying', 'sleeping'):
                        pos_mult = 2.0
                    elif position in ('sitting', 'kneeling', 'resting'):
                        pos_mult = 1.5
                    else:
                        pos_mult = 1.0

                    # Supernode: +50% on top of position mult
                    node_mult = 1.5 if supernode else 1.0

                    hp_regen = max(1, int(base_hp_regen * pos_mult * node_mult))

                    # Minor bleed (1-2 stacks) halves regen; 3+ already suppresses above
                    if is_bleeding and bleed_stacks > 0:
                        hp_regen = max(0, hp_regen // 2)

                    session.health_current = min(session.health_max,
                                                 session.health_current + hp_regen)

            # ── Mana regen ───────────────────────────────────────────────────
            if session.mana_max > 0 and session.mana_current < session.mana_max:
                int_bonus = (getattr(session, 'stat_intuition', 50) - 50) // 4
                spi_bonus = (getattr(session, 'stat_wisdom',    50) - 50) // 4
                base_mana_regen = max(1, 1 + int_bonus + spi_bonus)

                node_mult = 2.0 if is_node else 1.0
                mana_regen = max(1, int(base_mana_regen * node_mult))

                session.mana_current = min(session.mana_max,
                                           session.mana_current + mana_regen)

            # ── Stamina regen ─────────────────────────────────────────────────
            if session.stamina_current < session.stamina_max:
                con_bonus = (getattr(session, 'stat_constitution', 50) - 50) // 4
                base_sta_regen = max(1, 2 + con_bonus)

                # sleeping counts same as lying for stamina recovery
                if position in ('sitting', 'kneeling', 'lying', 'sleeping', 'resting'):
                    sta_mult = 1.5
                else:
                    sta_mult = 1.0

                sta_regen = max(1, int(base_sta_regen * sta_mult))
                session.stamina_current = min(session.stamina_max,
                                              session.stamina_current + sta_regen)

            # ── Spirit regen (supernode only, or sleeping) ────────────────────
            # GS4: spirit recovers naturally when sleeping or resting at a node.
            # Base: 1 spirit per pulse only when on a supernode or sleeping.
            if session.spirit_current < session.spirit_max:
                if supernode or position in ('sleeping', 'lying', 'resting'):
                    spirit_regen = 1
                    session.spirit_current = min(session.spirit_max,
                                                 session.spirit_current + spirit_regen)

            # Auto-clear minor injuries once health is full
            if session.health_current >= session.health_max:
                injuries = getattr(session, 'injuries', {})
                for loc in list(injuries.keys()):
                    if injuries[loc] <= 1:
                        del injuries[loc]
