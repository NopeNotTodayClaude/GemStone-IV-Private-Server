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
                    if hasattr(self.server, "fake_players"):
                        for actor in self.server.fake_players.get_all():
                            mult = getattr(actor, 'death_stat_mult', 1.0)
                            if mult < 1.0:
                                await self.server.death.stat_penalty_tick(actor)
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

        if hasattr(self.server, "pets"):
            try:
                await self.server.pets.tick(self.tick_count)
            except Exception as e:
                log.error("Pet tick error: %s", e, exc_info=True)

        if hasattr(self.server, "traps"):
            try:
                await self.server.traps.tick(self.tick_count)
            except Exception as e:
                log.error("Trap tick error: %s", e, exc_info=True)

        if hasattr(self.server, "ferries"):
            try:
                await self.server.ferries.tick(self.tick_count)
            except Exception as e:
                log.error("Ferry tick error: %s", e, exc_info=True)

        if hasattr(self.server, "travel_offices"):
            try:
                await self.server.travel_offices.tick(self.tick_count)
            except Exception as e:
                log.error("Travel office tick error: %s", e, exc_info=True)

        if hasattr(self.server, "justice"):
            try:
                await self.server.justice.tick(self.tick_count)
            except Exception as e:
                log.error("Justice tick error: %s", e, exc_info=True)

        if hasattr(self.server, "fake_players"):
            try:
                await self.server.fake_players.tick(self.tick_count)
            except Exception as e:
                log.error("Fake player tick error: %s", e, exc_info=True)

        if hasattr(self.server, "town_trouble"):
            try:
                await self.server.town_trouble.tick(self.tick_count)
            except Exception as e:
                log.error("Town trouble tick error: %s", e, exc_info=True)

        if hasattr(self.server, "spell_summons"):
            try:
                await self.server.spell_summons.tick(self.tick_count)
            except Exception as e:
                log.error("Spell summon tick error: %s", e, exc_info=True)

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
            buffs = {}
            try:
                db = getattr(self.server, "db", None)
                if db and getattr(session, "character_id", None):
                    buffs = db.get_active_buff_effect_totals(session.character_id) or {}
            except Exception:
                buffs = {}
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
                    hp_regen += int(buffs.get("regen_bonus", 0) or 0)

                    # Minor bleed (1-2 stacks) halves regen; 3+ already suppresses above
                    if is_bleeding and bleed_stacks > 0:
                        hp_regen = max(0, hp_regen // 2)

                    session.health_current = min(session.health_max,
                                                 session.health_current + hp_regen)

            # ── Mana regen ───────────────────────────────────────────────────
            effective_mana_max = int(session.mana_max or 0) + int(buffs.get("max_mana_bonus", 0) or 0)
            if effective_mana_max > 0 and session.mana_current < effective_mana_max:
                int_bonus = (getattr(session, 'stat_intuition', 50) - 50) // 4
                spi_bonus = (getattr(session, 'stat_wisdom',    50) - 50) // 4
                base_mana_regen = max(1, 1 + int_bonus + spi_bonus)

                node_mult = 2.0 if is_node else 1.0
                mana_regen = max(1, int(base_mana_regen * node_mult))

                session.mana_current = min(effective_mana_max,
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

            # Auto-clear trivial recovered wounds once health is full.
            # Legacy code only trimmed session.injuries, which let canonical
            # session.wounds + character_wounds resurrect those same wounds
            # on the next login.
            if session.health_current >= session.health_max:
                injuries = getattr(session, 'injuries', {})
                for loc in list(injuries.keys()):
                    if injuries[loc] <= 1:
                        del injuries[loc]

                wb = getattr(self.server, "wound_bridge", None)
                wounds = getattr(session, "wounds", {}) or {}
                if wb and wounds:
                    updated = {}
                    changed = False
                    for loc, entry in wounds.items():
                        if not isinstance(entry, dict):
                            changed = True
                            continue
                        cleaned = wb._clear_fully_recovered_minor_wound(session, entry)
                        if cleaned is None:
                            changed = True
                            continue
                        if cleaned != entry:
                            changed = True
                        updated[loc] = cleaned
                    if changed:
                        wb._set_wounds(session, updated)
                        wb.sync_session_state(session)
                        await wb.save_wounds(session)

            if buffs.get("wound_regen"):
                wb = getattr(self.server, "wound_bridge", None)
                wounds = getattr(session, "wounds", {}) or {}
                if wb and wounds:
                    ranked = [
                        (loc, max(int((entry or {}).get("wound_rank", 0) or 0),
                                  int((entry or {}).get("scar_rank", 0) or 0)))
                        for loc, entry in wounds.items()
                        if isinstance(entry, dict)
                    ]
                    ranked = [item for item in ranked if item[1] > 0]
                    if ranked:
                        ranked.sort(key=lambda item: item[1], reverse=True)
                        try:
                            wb.empath_heal(session, session, ranked[0][0])
                            await wb.save_wounds(session)
                        except Exception as e:
                            log.error("Wound regeneration pulse failed for %s: %s", getattr(session, "character_name", "?"), e)
