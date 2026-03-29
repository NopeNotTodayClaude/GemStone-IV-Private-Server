"""
EventManager — scheduled world event controller.

Reads scripts/data/events_config.lua for all tunable values.
Writes to / reads from the server_events DB table.
Hooks into the game_loop tick to check whether events should start or expire.
Sends broadcast announcements to online players when events fire.

Events:
  Gift of Lumnis   — Saturday midnight, per-character absorption bonus
  Bonus XP Event   — Sunday midnight, 24h server-wide kill XP multiplier
"""

import logging
import os
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

_HERE        = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_LUA_CFG     = os.path.join(_PROJECT_ROOT, "scripts", "data", "events_config.lua")


def _load_config() -> dict:
    """Parse events_config.lua → plain Python dict. Returns hardcoded defaults on error."""
    try:
        from lupa import LuaRuntime  # type: ignore
        lua = LuaRuntime(unpack_returned_tuples=True)
        with open(_LUA_CFG, "r", encoding="utf-8") as f:
            src = f.read()
        tbl = lua.execute(src)

        def _cvt(t):
            if t is None:
                return None
            if hasattr(t, "items"):
                items = list(t.items())
                if items and all(isinstance(k, int) for k, _ in items):
                    return [v for _, v in sorted(items)]
                return {k: _cvt(v) for k, v in items}
            return t

        return _cvt(tbl)
    except Exception as e:
        log.warning("events_config.lua load failed (%s) — using hardcoded defaults", e)
        return _DEFAULTS


# ── Hardcoded fallback (matches events_config.lua) ────────────────────────────
_DEFAULTS = {
    "lumnis": {
        "active_days":       [5],
        "start_hour":        0,
        "phase1_multiplier": 3,
        "phase2_multiplier": 2,
        "phase1_pool":       43800,
        "phase2_pool":       21900,
        "announce_login":    [
            "The silvery light of Lumnis shimmers through the ether.",
            "The Goddess smiles upon Elanthia this weekend!",
            "Your mind absorbs knowledge with extraordinary clarity.",
            "The Gift of Lumnis is underway!",
        ],
        "announce_start":    "A soft, silvery luminescence fills the sky.  The Gift of Lumnis has descended upon Elanthia!",
        "phase1_msg":        "The Gift of Lumnis empowers your learning — your mind absorbs experience at triple the normal rate!",
        "phase2_msg":        "The first gift of Lumnis fades slightly.  Your mind continues to absorb experience at double the normal rate.",
        "expired_msg":       "The Gift of Lumnis draws to a close.  Your mind returns to its normal pace of learning.",
    },
    "bonus_xp": {
        "active_days":       [6],
        "start_hour":        0,
        "duration_hours":    24,
        "multiplier":        2,
        "announce_login":    [
            "A surge of vital energy permeates the land.",
            "Creatures yield their secrets more freely today!",
            "You will earn bonus experience from every kill.",
            "The Sunday Bonus XP Event is underway!",
        ],
        "announce_start":    "A surge of vital energy sweeps across Elanthia!  Bonus experience is now active for the next 24 hours!",
        "announce_expired":  "The surge of vital energy fades.  Experience gains return to their normal rate.",
    },
    "combined_announce_login": [
        "The Gift of Lumnis shimmers in the air and vital energy surges through the land.",
        "The Goddess smiles upon Elanthia — and creatures yield their secrets more freely!",
        "Your mind absorbs knowledge swiftly, and every kill brings bonus experience.",
        "The Gift of Lumnis and the Sunday Bonus XP Event are both underway!",
    ],
}


class EventManager:
    """Manages scheduled world events. Registered on server as server.events."""

    # How often (in real seconds) to re-check event schedule
    CHECK_INTERVAL = 60.0

    def __init__(self, server):
        self.server = server
        self.cfg    = _load_config()
        self._last_check: float = 0.0
        # In-memory cache of DB state, refreshed each check
        self._lumnis_active:   bool  = False
        self._lumnis_started:  "datetime|None" = None
        self._bonus_xp_active: bool  = False
        self._bonus_xp_mult:   float = 1.0

    # ── Called from game_loop._tick() every 60s ───────────────────────────────

    async def tick(self, now: float):
        """Check schedule and fire/expire events. Called ~every 60 real seconds."""
        if now - self._last_check < self.CHECK_INTERVAL:
            return
        self._last_check = now

        try:
            dt = datetime.now()
            await self._check_lumnis(dt)
            await self._check_bonus_xp(dt)
            self._refresh_cache()
        except Exception as e:
            log.error("EventManager tick error: %s", e, exc_info=True)

    # ── Lumnis ────────────────────────────────────────────────────────────────

    async def _check_lumnis(self, dt: datetime):
        """Fire or expire the Gift of Lumnis based on current day/time."""
        cfg  = self.cfg.get("lumnis", _DEFAULTS["lumnis"])
        days = cfg.get("active_days", [5])         # 5=Sat (datetime.weekday())
        hour = int(cfg.get("start_hour", 0))

        db   = self.server.db
        if not db:
            return

        row = self._db_get_event("lumnis")
        is_active    = bool(row.get("is_active", 0)) if row else False
        started_at   = row.get("started_at") if row else None

        today        = dt.weekday()   # Mon=0 … Sun=6
        is_event_day = today in days
        past_start   = dt.hour >= hour

        # ── Should it be active? ──────────────────────────────────────────────
        if is_event_day and past_start:
            # Compute the start of this weekend's cycle (Saturday midnight)
            # so we know if this is a NEW cycle or a continuation
            days_since_sat = (today - 5) % 7   # days since the most recent Saturday
            cycle_start    = datetime(dt.year, dt.month, dt.day) - timedelta(days=days_since_sat)
            cycle_start    = cycle_start.replace(hour=0, minute=0, second=0, microsecond=0)

            if not is_active or started_at is None or \
               (isinstance(started_at, datetime) and started_at < cycle_start):
                # New cycle — activate and reset all character Lumnis state
                await self._activate_lumnis(cycle_start, cfg)
                return

        # ── Should it expire? ─────────────────────────────────────────────────
        if is_active and not is_event_day:
            await self._expire_lumnis(cfg)

    async def _activate_lumnis(self, cycle_start: datetime, cfg: dict):
        db = self.server.db
        if not db:
            return

        log.info("EventManager: Activating Gift of Lumnis (cycle start %s)", cycle_start)

        # Reset all character Lumnis state for the new cycle
        try:
            db.execute_update(
                "UPDATE characters SET lumnis_phase = 1, lumnis_bonus_earned = 0, "
                "lumnis_cycle_id = %s",
                (cycle_start,)
            )
        except Exception as e:
            log.error("Lumnis character reset failed: %s", e)

        # Also reset in-memory sessions
        for session in self.server.sessions.playing():
            session.lumnis_phase        = 1
            session.lumnis_bonus_earned = 0
            session.lumnis_cycle_id     = cycle_start

        # Write event row
        try:
            db.execute_update(
                "UPDATE server_events SET is_active=1, started_at=%s, expires_at=NULL, "
                "multiplier=%s, phase=1 WHERE event_type='lumnis'",
                (cycle_start, float(cfg.get("phase1_multiplier", 3)))
            )
        except Exception as e:
            log.error("Lumnis DB activate failed: %s", e)

        self._lumnis_active  = True
        self._lumnis_started = cycle_start

        # Broadcast to online players
        msg = cfg.get("announce_start", "The Gift of Lumnis has descended upon Elanthia!")
        await self._broadcast(msg, color_preset="EXPERIENCE")

    async def _expire_lumnis(self, cfg: dict):
        db = self.server.db
        if not db:
            return

        log.info("EventManager: Expiring Gift of Lumnis")
        try:
            db.execute_update(
                "UPDATE server_events SET is_active=0, expires_at=NOW(), phase=0 "
                "WHERE event_type='lumnis'"
            )
        except Exception as e:
            log.error("Lumnis DB expire failed: %s", e)

        self._lumnis_active = False

        # Tell all players their bonus ended
        msg = cfg.get("expired_msg", "The Gift of Lumnis draws to a close.")
        await self._broadcast(msg, color_preset="SYSTEM")

        # Zero out in-memory session phase so absorption goes back to normal immediately
        for session in self.server.sessions.playing():
            session.lumnis_phase = 0

    # ── Bonus XP ──────────────────────────────────────────────────────────────

    async def _check_bonus_xp(self, dt: datetime):
        cfg  = self.cfg.get("bonus_xp", _DEFAULTS["bonus_xp"])
        days = cfg.get("active_days", [6])
        hour = int(cfg.get("start_hour", 0))
        dur  = int(cfg.get("duration_hours", 24))

        db = self.server.db
        if not db:
            return

        row       = self._db_get_event("bonus_xp")
        is_active = bool(row.get("is_active", 0)) if row else False
        exp_at    = row.get("expires_at") if row else None

        today        = dt.weekday()
        is_event_day = today in days
        past_start   = dt.hour >= hour

        # Auto-expire if expiry timestamp passed
        if is_active and isinstance(exp_at, datetime) and dt >= exp_at:
            await self._expire_bonus_xp(cfg)
            return

        # Should activate?
        if is_event_day and past_start and not is_active:
            expires = datetime(dt.year, dt.month, dt.day,
                               hour, 0, 0) + timedelta(hours=dur)
            await self._activate_bonus_xp(expires, cfg)
            return

        # Should expire (wrong day, no expiry timestamp yet)?
        if is_active and not is_event_day:
            await self._expire_bonus_xp(cfg)

    async def _activate_bonus_xp(self, expires_at: datetime, cfg: dict):
        db = self.server.db
        if not db:
            return

        mult = float(cfg.get("multiplier", 2))
        log.info("EventManager: Activating Bonus XP event (mult=%.1fx, expires %s)",
                 mult, expires_at)
        try:
            db.execute_update(
                "UPDATE server_events SET is_active=1, started_at=NOW(), "
                "expires_at=%s, multiplier=%s, phase=0 WHERE event_type='bonus_xp'",
                (expires_at, mult)
            )
        except Exception as e:
            log.error("Bonus XP DB activate failed: %s", e)

        self._bonus_xp_active = True
        self._bonus_xp_mult   = mult

        msg = cfg.get("announce_start", "Bonus experience is now active!")
        await self._broadcast(msg, color_preset="EXPERIENCE")

    async def _expire_bonus_xp(self, cfg: dict):
        db = self.server.db
        if not db:
            return

        log.info("EventManager: Expiring Bonus XP event")
        try:
            db.execute_update(
                "UPDATE server_events SET is_active=0, expires_at=NOW(), multiplier=1.00 "
                "WHERE event_type='bonus_xp'"
            )
        except Exception as e:
            log.error("Bonus XP DB expire failed: %s", e)

        self._bonus_xp_active = False
        self._bonus_xp_mult   = 1.0

        msg = cfg.get("announce_expired", "Bonus experience has ended.")
        await self._broadcast(msg, color_preset="SYSTEM")

    # ── Public API used by ExperienceManager ──────────────────────────────────

    def get_lumnis_absorption_multiplier(self, session) -> float:
        """
        Returns the Lumnis absorption multiplier for a specific session.
        Checks the session's lumnis_phase and whether the global event is active.
        Returns 1.0 if Lumnis is inactive or character's pool is exhausted.
        """
        if not self._lumnis_active:
            return 1.0
        phase = getattr(session, "lumnis_phase", 0)
        cfg   = self.cfg.get("lumnis", _DEFAULTS["lumnis"])
        if phase == 1:
            return float(cfg.get("phase1_multiplier", 3))
        elif phase == 2:
            return float(cfg.get("phase2_multiplier", 2))
        return 1.0

    def get_bonus_xp_multiplier(self) -> float:
        """Returns the current server-wide kill XP multiplier (1.0 if no event)."""
        return self._bonus_xp_mult if self._bonus_xp_active else 1.0

    async def on_lumnis_absorbed(self, session, amount_absorbed_at_bonus: int):
        """
        Called by ExperienceManager after each absorption tick with the BONUS
        portion of XP absorbed (i.e. extra XP above normal rate).
        Advances the character through Lumnis phases / exhaustion.
        """
        if not self._lumnis_active:
            return

        phase = getattr(session, "lumnis_phase", 0)
        if phase == 0:
            return

        cfg = self.cfg.get("lumnis", _DEFAULTS["lumnis"])
        earned = getattr(session, "lumnis_bonus_earned", 0) + amount_absorbed_at_bonus
        session.lumnis_bonus_earned = earned

        p1_pool = int(cfg.get("phase1_pool", 43800))
        p2_pool = int(cfg.get("phase2_pool", 21900))
        total_pool = p1_pool + p2_pool

        if phase == 1 and earned >= p1_pool:
            # Phase 1 exhausted — drop to phase 2
            session.lumnis_phase = 2
            msg = cfg.get("phase2_msg", "The first gift of Lumnis fades slightly.")
            await session.send_line(f"\r\n  {msg}\r\n")
            log.info("Lumnis phase 2 for %s (earned %d)", session.character_name, earned)

        elif phase == 2 and earned >= total_pool:
            # Both pools exhausted — done for this cycle
            session.lumnis_phase = 0
            msg = cfg.get("expired_msg", "The Gift of Lumnis draws to a close.")
            await session.send_line(f"\r\n  {msg}\r\n")
            log.info("Lumnis exhausted for %s (earned %d)", session.character_name, earned)

        # Persist to DB
        db = self.server.db
        if db and session.character_id:
            try:
                db.execute_update(
                    "UPDATE characters SET lumnis_phase=%s, lumnis_bonus_earned=%s "
                    "WHERE id=%s",
                    (session.lumnis_phase, session.lumnis_bonus_earned, session.character_id)
                )
            except Exception as e:
                log.debug("Lumnis persist error: %s", e)

    def get_login_announcement(self) -> "list | str | None":
        """
        Returns the appropriate event announcement for a player logging in,
        or None if no events are active.
        Returns a list of lines if the config provides one, or a plain string.
        """
        cfg         = self.cfg
        lumnis_on   = self._lumnis_active
        bonus_on    = self._bonus_xp_active

        if lumnis_on and bonus_on:
            return cfg.get("combined_announce_login",
                           _DEFAULTS["combined_announce_login"])
        elif lumnis_on:
            return cfg.get("lumnis", {}).get(
                "announce_login", _DEFAULTS["lumnis"]["announce_login"])
        elif bonus_on:
            return cfg.get("bonus_xp", {}).get(
                "announce_login", _DEFAULTS["bonus_xp"]["announce_login"])
        return None

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _refresh_cache(self):
        """Re-read DB event rows into memory cache."""
        db = self.server.db
        if not db:
            return
        try:
            lumnis_row    = self._db_get_event("lumnis")
            bonus_row     = self._db_get_event("bonus_xp")
            self._lumnis_active   = bool(lumnis_row.get("is_active", 0)) if lumnis_row else False
            self._lumnis_started  = lumnis_row.get("started_at") if lumnis_row else None
            self._bonus_xp_active = bool(bonus_row.get("is_active", 0)) if bonus_row else False
            self._bonus_xp_mult   = float(bonus_row.get("multiplier", 1.0)) if bonus_row else 1.0
        except Exception as e:
            log.debug("EventManager cache refresh error: %s", e)

    def _db_get_event(self, event_type: str) -> dict:
        """Fetch one row from server_events. Returns {} on error."""
        db = self.server.db
        if not db:
            return {}
        try:
            rows = db.execute_query(
                "SELECT event_type, is_active, started_at, expires_at, multiplier, phase "
                "FROM server_events WHERE event_type = %s",
                (event_type,)
            )
            if rows:
                cols = ("event_type", "is_active", "started_at", "expires_at", "multiplier", "phase")
                return dict(zip(cols, rows[0]))
        except Exception as e:
            log.debug("EventManager DB read error for %s: %s", event_type, e)
        return {}

    async def _broadcast(self, message: str, color_preset: str = "SYSTEM"):
        """Send a message to all online players."""
        try:
            from server.core.protocol.colors import colorize, TextPresets
            preset = getattr(TextPresets, color_preset, TextPresets.SYSTEM)
            for session in self.server.sessions.playing():
                await session.send_line("")
                await session.send_line(colorize(f"  ** {message} **", preset))
                await session.send_line("")
        except Exception as e:
            log.error("EventManager broadcast error: %s", e)
