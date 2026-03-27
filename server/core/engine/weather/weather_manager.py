"""
WeatherManager
Zone-level weather state machine. One weather state per zone.

- Reads scripts/data/weather_config.lua for all rules
- Persists state to server_weather DB table
- Ticks every ~5 minutes (configurable in weather_config.lua)
- Sends ambient weather messages to outdoor rooms
- Exposes force_weather() for weather charm / GM use
- Exposes get_zone_weather() for item scripts and foraging

Public API (registered on server as server.weather):
    state = server.weather.get_zone_weather(zone_id)
      -> {"state": "rain", "intensity": "heavy", "forced_by": None, ...}

    server.weather.force_weather(zone_id, state, intensity, duration_seconds, forced_by)
      -> Forces weather for a zone; reverts naturally when duration expires

    period_id = server.weather.get_time_period()
      -> "morning", "evening", "night", etc.  (from ElanthianClock)
"""

import logging
import os
import random
import time as _time
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

_HERE         = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_LUA_CFG      = os.path.join(_PROJECT_ROOT, "scripts", "data", "weather_config.lua")


def _load_config() -> dict:
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
                    return [_cvt(v) for _, v in sorted(items)]
                return {str(k): _cvt(v) for k, v in items}
            return t

        return _cvt(tbl)
    except Exception as e:
        log.warning("weather_config.lua load failed (%s) — using minimal defaults", e)
        return {"states": {}, "climates": {}, "global_messages": {},
                "tick_interval_seconds": 300}


class WeatherManager:
    """Manages zone weather states. Registered on server as server.weather."""

    def __init__(self, server):
        self.server   = server
        self.cfg      = _load_config()
        self._tick_interval = float(
            self.cfg.get("tick_interval_seconds", 300)
        )
        self._last_tick: float = 0.0
        # In-memory cache: zone_id -> {state, intensity, forced_by, forced_until}
        self._zone_cache: dict = {}
        # Zone climate cache: zone_id -> climate string
        self._zone_climates: dict = {}

    async def initialize(self):
        """Called once after server starts. Loads existing weather from DB."""
        self._load_zone_climates()
        self._load_weather_from_db()
        log.info("WeatherManager initialized (%d zones tracked)", len(self._zone_cache))

    # ── Called from game_loop._tick() ─────────────────────────────────────────

    async def tick(self, now: float):
        """Called every server tick. Only does work every tick_interval seconds."""
        if now - self._last_tick < self._tick_interval:
            return
        self._last_tick = now

        try:
            await self._weather_tick()
        except Exception as e:
            log.error("WeatherManager tick error: %s", e, exc_info=True)

    async def _weather_tick(self):
        """For each zone: check if forced weather expired, then maybe transition."""
        now_dt = datetime.now()
        climates_cfg = self.cfg.get("climates", {})

        for zone_id, state_data in list(self._zone_cache.items()):
            # ── Check forced weather expiry ────────────────────────────────
            forced_until = state_data.get("forced_until")
            if forced_until and isinstance(forced_until, datetime) and now_dt >= forced_until:
                state_data["forced_by"]    = None
                state_data["forced_until"] = None
                self._db_update_zone(zone_id, state_data)
                log.debug("Zone %d forced weather expired, returning to natural", zone_id)

            # Don't tick forced weather
            if state_data.get("forced_by"):
                continue

            # ── Natural weather transition ─────────────────────────────────
            climate_name = self._get_zone_climate(zone_id)
            climate_cfg  = climates_cfg.get(climate_name, {})

            # Skip non-weather climates
            if climate_name == "underground":
                continue

            change_chance = int(climate_cfg.get("change_chance", 20))
            if random.randint(1, 100) > change_chance:
                continue   # no change this tick

            current_state = state_data.get("state", "clear")
            transitions   = climate_cfg.get("transitions", {})
            next_state    = self._pick_next_state(current_state, transitions, climate_cfg)

            if next_state and next_state != current_state:
                old_state = current_state
                state_data["state"]     = next_state
                state_data["intensity"] = self._pick_intensity(next_state)
                self._db_update_zone(zone_id, state_data)
                log.debug("Zone %d weather: %s → %s", zone_id, old_state, next_state)

                # Send ambient message to players in this zone
                await self._broadcast_weather_message(zone_id, next_state, state_data.get("intensity"))

    def _pick_next_state(self, current: str, transitions: dict, climate_cfg: dict) -> str:
        """Weighted random choice from transition table."""
        trans = transitions.get(current, {})
        if not trans:
            # No transition defined — pick from allowed states randomly
            allowed = climate_cfg.get("allowed_states", ["clear"])
            if isinstance(allowed, dict):
                allowed = list(allowed.values())
            return random.choice(allowed) if allowed else current

        if isinstance(trans, dict):
            states  = list(trans.keys())
            weights = [int(trans[s]) for s in states]
            return random.choices(states, weights=weights, k=1)[0]
        return current

    def _pick_intensity(self, state: str) -> "str | None":
        """Return a random intensity for states that have one, or None."""
        state_cfg = self.cfg.get("states", {}).get(state, {})
        if isinstance(state_cfg, dict) and state_cfg.get("has_intensity"):
            return random.choice(["light", "moderate", "heavy"])
        return None

    # ── Ambient weather messaging ─────────────────────────────────────────────

    async def _broadcast_weather_message(self, zone_id: int, state: str, intensity: "str|None"):
        """Send a weather ambient message to all outdoor players in this zone."""
        # Get message pool — zone override first, then global fallback
        msg = self._pick_weather_message(zone_id, state)
        if not msg:
            return

        try:
            state_cfg     = self.cfg.get("states", {}).get(state, {})
            outdoor_only  = state_cfg.get("outdoor_only", True) if isinstance(state_cfg, dict) else True

            for session in self.server.sessions.playing():
                room = session.current_room
                if not room:
                    continue
                if getattr(room, "zone_id", None) != zone_id:
                    continue
                if outdoor_only and getattr(room, "indoor", False):
                    continue
                await session.send_line(f"  {msg}")
        except Exception as e:
            log.debug("Weather broadcast error zone %d: %s", zone_id, e)

    def _pick_weather_message(self, zone_id: int, state: str) -> "str|None":
        """Pick a random message for the given weather state. Zone pool first."""
        # Try zone LUA weather_messages override (loaded via zone manager)
        zone_messages = self._get_zone_weather_messages(zone_id, state)
        if zone_messages:
            return random.choice(zone_messages)

        # Fall back to global pool from weather_config.lua
        global_msgs = self.cfg.get("global_messages", {})
        pool        = global_msgs.get(state, [])
        if isinstance(pool, dict):
            pool = list(pool.values())
        return random.choice(pool) if pool else None

    def _get_zone_weather_messages(self, zone_id: int, state: str) -> list:
        """Return zone-specific weather messages if defined in zone LUA."""
        try:
            zone = self.server.world.get_zone_by_id(zone_id)
            if zone and hasattr(zone, "weather_messages"):
                pool = zone.weather_messages.get(state, [])
                return pool if pool else []
        except Exception:
            pass
        return []

    # ── Public API ────────────────────────────────────────────────────────────

    def get_zone_weather(self, zone_id: int) -> dict:
        """
        Returns the current weather state dict for a zone.
        {"state": "rain", "intensity": "heavy", "forced_by": None, "forced_until": None}
        Falls back to "clear" for unknown zones.
        """
        if zone_id not in self._zone_cache:
            climate = self._get_zone_climate(zone_id)
            climates_cfg = self.cfg.get("climates", {})
            default = climates_cfg.get(climate, {}).get("default_state", "clear")
            self._zone_cache[zone_id] = {
                "state": default, "intensity": None,
                "forced_by": None, "forced_until": None,
            }
        return dict(self._zone_cache[zone_id])

    def get_room_weather(self, room) -> dict:
        """
        Returns weather for the zone the room belongs to.
        Returns {"state": "still"} for indoor or underground rooms.
        """
        if getattr(room, "indoor", False):
            return {"state": "still", "intensity": None, "forced_by": None, "forced_until": None}
        zone_id = getattr(room, "zone_id", None)
        if zone_id is None:
            return {"state": "clear", "intensity": None, "forced_by": None, "forced_until": None}
        climate = self._get_zone_climate(zone_id)
        if climate == "underground":
            return {"state": "still", "intensity": None, "forced_by": None, "forced_until": None}
        return self.get_zone_weather(zone_id)

    def get_weather_label(self, zone_id: int) -> str:
        """Human-readable weather label e.g. 'heavily raining'."""
        w = self.get_zone_weather(zone_id)
        state = w.get("state", "clear")
        states_cfg = self.cfg.get("states", {})
        label = states_cfg.get(state, {}).get("label", state.replace("_", " ")) \
                if isinstance(states_cfg.get(state), dict) else state.replace("_", " ")
        intensity = w.get("intensity")
        if intensity and intensity != "moderate":
            return f"{intensity}ly {label}"
        return label

    def force_weather(self, zone_id: int, state: str, intensity: "str|None" = None,
                      duration_seconds: int = 7200, forced_by: str = "charm"):
        """
        Force weather state for a zone. Used by weather charm and events.
        Reverts to natural after duration_seconds.
        duration_seconds=0 means permanent until manually cleared.
        """
        climates_cfg   = self.cfg.get("climates", {})
        climate        = self._get_zone_climate(zone_id)
        climate_cfg    = climates_cfg.get(climate, {})
        allowed        = climate_cfg.get("allowed_states", [])
        if isinstance(allowed, dict):
            allowed = list(allowed.values())

        # Validate state — charm-only states always allowed regardless of climate
        state_cfg   = self.cfg.get("states", {}).get(state, {})
        charm_only  = state_cfg.get("charm_only", False) if isinstance(state_cfg, dict) else False
        if not charm_only and state not in allowed and state != "still":
            log.warning("force_weather: state %r not allowed for climate %r in zone %d",
                        state, climate, zone_id)
            # Allow it anyway — items can force unusual weather

        forced_until = (datetime.now() + timedelta(seconds=duration_seconds)
                        ) if duration_seconds > 0 else None

        self._zone_cache[zone_id] = {
            "state":        state,
            "intensity":    intensity,
            "forced_by":    forced_by,
            "forced_until": forced_until,
        }
        self._db_update_zone(zone_id, self._zone_cache[zone_id])
        log.info("WeatherManager: zone %d forced to %r by %s (expires %s)",
                 zone_id, state, forced_by, forced_until)

    def clear_forced_weather(self, zone_id: int):
        """Remove a forced weather override and return to natural progression."""
        data = self._zone_cache.get(zone_id, {})
        data["forced_by"]    = None
        data["forced_until"] = None
        self._zone_cache[zone_id] = data
        self._db_update_zone(zone_id, data)

    def get_time_period(self) -> str:
        """Convenience: returns current Elanthian time period_id."""
        from server.core.engine.time.elanthian_clock import ElanthianClock
        return ElanthianClock.period_id()

    def is_precipitation(self, zone_id: int) -> bool:
        """True if the zone is currently getting precipitation (rain/snow/etc.)."""
        w         = self.get_zone_weather(zone_id)
        state     = w.get("state", "clear")
        states_cfg = self.cfg.get("states", {})
        return states_cfg.get(state, {}).get("precipitation", False) \
               if isinstance(states_cfg.get(state), dict) else False

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_zone_climate(self, zone_id: int) -> str:
        if zone_id in self._zone_climates:
            return self._zone_climates[zone_id]
        # Try to get from loaded zone object
        try:
            zone = self.server.world.get_zone_by_id(zone_id)
            if zone:
                climate = getattr(zone, "climate", "temperate") or "temperate"
                self._zone_climates[zone_id] = climate
                return climate
        except Exception:
            pass
        return "temperate"

    def _load_zone_climates(self):
        """Pre-cache climates for all known zones."""
        try:
            for zone in self.server.world.get_all_zones():
                zid = getattr(zone, "id", None) or getattr(zone, "zone_id", None)
                if zid:
                    self._zone_climates[zid] = getattr(zone, "climate", "temperate") or "temperate"
        except Exception as e:
            log.debug("Could not pre-cache zone climates: %s", e)

    def _load_weather_from_db(self):
        """Load persisted weather states from server_weather table."""
        db = self.server.db
        if not db:
            return
        try:
            rows = db.execute_query(
                "SELECT zone_id, weather_state, intensity, forced_by, forced_until "
                "FROM server_weather"
            )
            for row in rows:
                zone_id, state, intensity, forced_by, forced_until = row
                self._zone_cache[int(zone_id)] = {
                    "state":        state or "clear",
                    "intensity":    intensity,
                    "forced_by":    forced_by,
                    "forced_until": forced_until,
                }
            log.info("WeatherManager: loaded %d zone states from DB", len(rows))
        except Exception as e:
            log.warning("Could not load weather from DB: %s", e)

    def _db_update_zone(self, zone_id: int, data: dict):
        """Upsert a zone's weather state into DB."""
        db = self.server.db
        if not db:
            return
        try:
            db.execute_update(
                """
                INSERT INTO server_weather
                    (zone_id, weather_state, intensity, forced_by, forced_until)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    weather_state = VALUES(weather_state),
                    intensity     = VALUES(intensity),
                    forced_by     = VALUES(forced_by),
                    forced_until  = VALUES(forced_until)
                """,
                (
                    zone_id,
                    data.get("state", "clear"),
                    data.get("intensity"),
                    data.get("forced_by"),
                    data.get("forced_until"),
                )
            )
        except Exception as e:
            log.debug("WeatherManager DB update error zone %d: %s", zone_id, e)
