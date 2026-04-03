"""
status_manager.py
-----------------
GemStone IV Status Effect Manager.

This is the single source of truth for all status effects on every entity
(players and creatures).  It replaces the ad-hoc in_combat boolean and the
older status_effects.py approach with a proper timed-effect engine driven
by the Lua data registry at scripts/data/status_effects.lua.

Public API (call these from combat, commands, spells, etc.):
    from server.core.engine.status_manager import StatusManager
    # Access via server.status:
    server.status.apply(entity, "stunned", duration=10)
    server.status.remove(entity, "stunned")
    server.status.has(entity, "stunned")
    server.status.get_combat_mods(entity)       -> (as_mod, ds_mod, evade_pct, parry_pct, block_pct)
    server.status.is_blocked(entity, "hide")    -> bool
    server.status.enter_combat(session, target)
    server.status.refresh_combat(session, target, duration=8)
    server.status.exit_combat(session, reason="clear")
    server.status.get_prompt_string(entity)     -> e.g. "[S!P]"
    server.status.status_list(entity)           -> list of display dicts
    await server.status.tick(tick_count)

in_combat state fix
-------------------
Previously in_combat was a raw boolean that various code paths set to True
but only inconsistently reset to False — causing the "still in combat after
kill" bug and the spurious "You flee from combat!" on room transitions.

Now:
  - in_combat is a timed STATUS EFFECT with an 8-second duration.
  - It is refreshed (re-applied) on every attack by or against the player.
  - When it expires, _on_expire checks whether any alive hostile creature in
    the room is still targeting the player.  If yes, it re-applies itself.
    If no, it sends "The combat area is clear." and clears session.in_combat.
  - session.in_combat and session.target are always kept in sync by this
    manager; no other code should touch them directly.

sleep / position states
-----------------------
sleeping, sitting, kneeling, resting, and prone are now formal STATUS EFFECTS
with duration=-1 (indefinite).  Position-checking code should use
server.status.has(entity, "sleeping") etc., or read session.position which
is still kept in sync for backward compatibility.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger(__name__)


# Status effect definitions are loaded exclusively from scripts/data/status_effects.lua
# There is no Python fallback — if Lua fails to load, StatusManager.initialize()
# will log CRITICAL and raise.  Fix the Lua file.
# This dict is populated by initialize() and must never be manually populated here.
_FALLBACK_DEFS: Dict[str, dict] = {}   # intentionally empty

# Effects that should NOT be logged when applied (too spammy)
_SILENT_EFFECTS = {"in_combat", "exited_combat", "roundtime", "recent_block",
                   "recent_parry", "recent_evade"}

# Expire messages shown to players
_EXPIRE_MESSAGES = {
    "stunned":        "  Your head clears.  You are no longer stunned.",
    "webbed":         "  The webs binding you dissolve.  You are free.",
    "rooted":         "  You regain control of your limbs.",
    "immobile":       "  You can move again.",
    "silenced":       "  Your voice returns.",
    "staggered":      "  You regain your footing.",
    "blinded":        "  Your vision returns.",
    "slowed":         "  Your movements return to normal speed.",
    "demoralized":    "  You steel yourself and regain your confidence.",
    "feeble":         "  Your strength returns.",
    "clumsy":         "  Your coordination returns.",
    "dazed":          "  Your head clears.",
    "disoriented":    "  You regain your bearings.",
    "overexerted":    "  Your stamina recovers.",
    "vulnerable":     "  Your defenses solidify.",
    "calmed":         "  The calming sensation fades.  Your aggression returns.",
    "fear":           "  You regain your nerve.",
    "terrified":      "  The terror fades.  You can think clearly again.",
    "sheer_fear":     "  The paralytic fear releases its grip on you.",
    "poisoned":       "  The poison fades from your system.",
    "major_poison":   "  The poison clears from your body.",
    "disease":        "  The disease runs its course.",
    "groggy":         "  The grogginess fades.",
    "wounded":        "  Your body's natural recovery resumes.",
    "unconscious":    "  You regain consciousness.",
}


class StatusEffect:
    """One active status effect instance on an entity."""

    __slots__ = ("effect_id", "expires", "stacks", "magnitude",
                 "last_tick", "tick_interval", "source", "data")

    def __init__(self, effect_id: str, expires: float, stacks: int,
                 magnitude: float, tick_interval: float, source=None, data: dict = None):
        self.effect_id    = effect_id
        self.expires      = expires       # unix timestamp; -1 = indefinite
        self.stacks       = stacks
        self.magnitude    = magnitude
        self.last_tick    = time.time()
        self.tick_interval = tick_interval
        self.source       = source        # entity that applied this (or None)
        self.data         = data or {}    # arbitrary extra payload

    @property
    def active(self) -> bool:
        return self.expires < 0 or time.time() < self.expires

    @property
    def remaining(self) -> float:
        if self.expires < 0:
            return -1
        return max(0.0, self.expires - time.time())


class StatusManager:
    """
    Central status effect engine.  One instance lives on the server as
    server.status (wired in game_server.py).

    Thread safety: all calls from the async event loop — no locking needed.
    """

    def __init__(self, server):
        self._server = server
        self._defs: Dict[str, dict] = {}   # populated by initialize() from Lua
        self._lua_loaded = False

    # ── Initialisation ────────────────────────────────────────────────────────

    async def initialize(self):
        """Load effect definitions from scripts/data/status_effects.lua.
        Raises RuntimeError if Lua is unavailable or the file fails to load.
        There is no Python fallback — fix the Lua file if this fires.
        """
        self._defs = {}
        try:
            lua = getattr(self._server, "lua", None)
            engine = getattr(lua, "engine", None) if lua else None
            if not engine or not engine.available:
                raise RuntimeError(
                    "StatusManager: Lua engine not available. "
                    "Cannot load status_effects.lua. Check lupa installation and scripts path."
                )

            raw = engine.load_data("data/status_effects")
            if isinstance(raw, tuple):
                from server.core.scripting.lua_engine import lua_to_python
                resolved = None
                for candidate in raw:
                    converted = (
                        lua_to_python(candidate)
                        if not isinstance(candidate, (dict, list))
                        else candidate
                    )
                    if isinstance(converted, dict) and converted:
                        resolved = converted
                        break
                raw = resolved
            if isinstance(raw, list):
                raw = {i: v for i, v in enumerate(raw) if v is not None}

            if not raw:
                raise RuntimeError(
                    "StatusManager: status_effects.lua returned empty data. "
                    "Check the Lua file for syntax errors."
                )

            merged = {}
            for k, v in raw.items():
                if isinstance(v, dict):
                    if "blocks" in v and not isinstance(v["blocks"], list):
                        try:
                            v["blocks"] = list(v["blocks"].values()) if hasattr(v["blocks"], "values") else list(v["blocks"])
                        except Exception:
                            v["blocks"] = []
                    cm = v.get("combat_mods", {})
                    if not isinstance(cm, dict):
                        try:
                            cm = dict(cm.items()) if hasattr(cm, "items") else {}
                        except Exception:
                            cm = {}
                    v["combat_mods"] = cm
                    merged[k] = v

            if not merged:
                raise RuntimeError(
                    "StatusManager: status_effects.lua parsed but produced no valid effect defs. "
                    "Check the Lua file structure."
                )

            self._defs = merged
            self._lua_loaded = True
            log.info("StatusManager: loaded %d effect defs from status_effects.lua", len(self._defs))

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(
                f"StatusManager: failed to load status_effects.lua: {e}"
            ) from e

    def get_def(self, effect_id: str) -> Optional[dict]:
        return self._defs.get(effect_id)

    # ── Core apply / remove / query ───────────────────────────────────────────

    def apply(self, entity, effect_id: str, duration: float = None,
              stacks: int = 1, magnitude: float = 1.0, source=None, **kwargs) -> bool:
        """
        Apply or refresh a status effect on entity.

        duration: seconds; None = use def default; -1 = indefinite.
        Returns True if the effect was newly applied, False if refreshed.
        """
        defn = self._defs.get(effect_id)
        if not defn:
            log.debug("StatusManager.apply: unknown effect '%s'", effect_id)
            return False

        if not hasattr(entity, "status_effects") or entity.status_effects is None:
            entity.status_effects = {}

        now = time.time()
        max_stacks = defn.get("max_stacks", 1)
        tick_iv    = defn.get("tick_interval", 0)

        if duration is None:
            duration = defn.get("duration_default", 30)

        expires = -1 if duration < 0 else (now + duration)
        newly_applied = effect_id not in entity.status_effects

        if effect_id in entity.status_effects:
            existing = entity.status_effects[effect_id]
            # Stuns: cannot be refreshed / extended (GS4 canonical)
            if effect_id == "stunned":
                return False
            # Refresh expiry only if new duration is longer
            if expires > 0:
                existing.expires = max(existing.expires, expires) if existing.expires > 0 else expires
            existing.stacks    = min(max_stacks, existing.stacks + stacks)
            existing.magnitude = max(existing.magnitude, magnitude)
        else:
            entity.status_effects[effect_id] = StatusEffect(
                effect_id    = effect_id,
                expires      = expires,
                stacks       = min(max_stacks, stacks),
                magnitude    = magnitude,
                tick_interval = tick_iv,
                source       = source,
                data         = kwargs,
            )

        # Sync position / in_combat booleans for backward compat
        self._sync_entity_flags(entity, effect_id, True)

        return newly_applied

    def remove(self, entity, effect_id: str):
        """Remove a specific status effect."""
        if not hasattr(entity, "status_effects") or not entity.status_effects:
            return
        entity.status_effects.pop(effect_id, None)
        self._sync_entity_flags(entity, effect_id, False)

    def has(self, entity, effect_id: str) -> bool:
        """Return True if entity has an active instance of this effect."""
        effects = getattr(entity, "status_effects", None)
        if not effects or effect_id not in effects:
            return False
        se = effects[effect_id]
        return se.active

    def get_effect(self, entity, effect_id: str) -> Optional[StatusEffect]:
        """Return the StatusEffect instance or None."""
        effects = getattr(entity, "status_effects", None)
        if not effects:
            return None
        se = effects.get(effect_id)
        return se if se and se.active else None

    def get_all_active(self, entity) -> List[StatusEffect]:
        """Return all currently active StatusEffect instances."""
        effects = getattr(entity, "status_effects", None)
        if not effects:
            return []
        return [se for se in effects.values() if se.active]

    def clear_all(self, entity, category: str = None):
        """Clear all effects (or only those in a given category)."""
        effects = getattr(entity, "status_effects", None)
        if not effects:
            return
        if category is None:
            entity.status_effects = {}
        else:
            to_remove = [eid for eid, se in effects.items()
                         if self._defs.get(eid, {}).get("category") == category]
            for eid in to_remove:
                effects.pop(eid, None)

    # ── Combat mods ──────────────────────────────────────────────────────────

    def get_combat_mods(self, entity) -> Tuple[int, int, int, int, int]:
        """
        Sum all active effect combat modifiers.
        Returns (as_mod, ds_mod, evade_pct_pen, parry_pct_pen, block_pct_pen).
        _pct values are additive reductions (positive = worse for defender).
        """
        as_mod = ds_mod = evade_pct = parry_pct = block_pct = 0
        for se in self.get_all_active(entity):
            cm = self._defs.get(se.effect_id, {}).get("combat_mods", {})
            scale = float(getattr(se, "magnitude", 1.0) or 1.0)
            stacks = max(1, int(getattr(se, "stacks", 1) or 1))
            factor = scale * stacks
            as_mod     += int((cm.get("as", 0) or 0) * factor)
            ds_mod     += int((cm.get("ds", 0) or 0) * factor)
            evade_pct  += int((cm.get("evade_pct", 0) or 0) * factor)
            parry_pct  += int((cm.get("parry_pct", 0) or 0) * factor)
            block_pct  += int((cm.get("block_pct", 0) or 0) * factor)
        return as_mod, ds_mod, evade_pct, parry_pct, block_pct

    # ── Action blocking ───────────────────────────────────────────────────────

    def is_blocked(self, entity, action: str) -> Optional[str]:
        """
        Return the name of the first effect that blocks <action>, or None.
        action: one of "actions", "movement", "speech", "hide", "cast",
                        "sleep", "rest"
        """
        for se in self.get_all_active(entity):
            blocks = self._defs.get(se.effect_id, {}).get("blocks", [])
            if action in blocks:
                return se.effect_id
        return None

    # ── in_combat state management (THE FIX) ─────────────────────────────────

    def enter_combat(self, entity, target, duration: float = 8.0):
        """
        Mark entity as entering combat.
        Sets session.in_combat True for backward compat.
        """
        self.apply(entity, "in_combat", duration=duration, source=target)
        entity.in_combat = True
        entity.target    = target
        # Break hidden state on combat entry
        if self.has(entity, "hidden"):
            self.remove(entity, "hidden")

    def refresh_combat(self, entity, target=None, duration: float = 8.0):
        """
        Refresh the combat timer.  Call this on every attack (by or against).
        """
        se = entity.status_effects.get("in_combat") if hasattr(entity, "status_effects") and entity.status_effects else None
        if se:
            se.expires = time.time() + duration
        else:
            self.apply(entity, "in_combat", duration=duration, source=target)
        entity.in_combat = True
        if target:
            entity.target = target

    def exit_combat(self, entity, reason: str = "clear"):
        """
        Cleanly exit combat.  Clears in_combat, sets exited_combat grace period.
        The exited_combat status suppresses "You flee from combat!" messages.
        """
        self.remove(entity, "in_combat")
        entity.in_combat = False
        entity.target    = None
        # Brief grace period so movement commands don't fire flee messaging
        self.apply(entity, "exited_combat", duration=3)

    # ── Prompt string ─────────────────────────────────────────────────────────

    def get_prompt_string(self, entity) -> str:
        """
        Build the GS4-style status prompt string, e.g. "[S!P]".
        Mirrors the official status prompt chars from the wiki.
        """
        chars = []
        seen  = set()
        for se in self.get_all_active(entity):
            ch = self._defs.get(se.effect_id, {}).get("prompt_char")
            if ch and ch not in seen:
                chars.append(ch)
                seen.add(ch)
        return "[" + "".join(chars) + "]" if chars else ""

    # ── STATUS command display ────────────────────────────────────────────────

    def status_list(self, entity) -> List[dict]:
        """
        Return a list of dicts for display in the STATUS command.
        Each dict: {name, category, remaining_str, stacks}
        """
        rows = []
        for se in sorted(self.get_all_active(entity),
                         key=lambda s: s.effect_id):
            defn = self._defs.get(se.effect_id, {})
            if se.remaining < 0:
                rem_str = "indefinite"
            elif se.remaining > 60:
                rem_str = f"{int(se.remaining // 60)}m {int(se.remaining % 60)}s"
            else:
                rem_str = f"{int(se.remaining)}s"
            rows.append({
                "name":      defn.get("name", se.effect_id),
                "category":  defn.get("category", "?"),
                "remaining": rem_str,
                "stacks":    se.stacks,
                "desc":      defn.get("description", ""),
            })
        return rows

    # ── Game loop tick ────────────────────────────────────────────────────────

    async def tick(self, tick_count: int):
        """
        Called every game tick (0.1s).  Processes effect timers every ~2s.
        DOT ticks (bleed/poison) run on their own per-effect intervals.
        """
        if tick_count % 20 != 0:
            return

        now = time.time()

        # Tick players
        sessions = list(self._server.world.get_all_players())
        if hasattr(self._server, "fake_players"):
            sessions.extend(self._server.fake_players.get_all())
        for session in sessions:
            if not session.connected or session.state != "playing":
                continue
            await self._tick_entity(session, now, is_player=True)

        # Tick creatures
        if hasattr(self._server, "creatures"):
            for creature in list(self._server.creatures._creatures.values()):
                if not creature.alive:
                    continue
                await self._tick_entity(creature, now, is_player=False)

    async def _tick_entity(self, entity, now: float, is_player: bool):
        """Process all effects on one entity."""
        # Dead players are immune — no DOTs, no ticking at all until revived
        if is_player and getattr(entity, "is_dead", False):
            return

        effects = getattr(entity, "status_effects", None)
        if not effects:
            return

        expired = []
        for eid, se in list(effects.items()):
            # Expiry
            if se.expires >= 0 and now >= se.expires:
                expired.append(eid)
                continue

            # Per-effect tick
            if se.tick_interval > 0 and (now - se.last_tick) >= se.tick_interval:
                se.last_tick = now
                await self._do_effect_tick(entity, eid, se, is_player)

        # Expire collected effects
        for eid in expired:
            effects.pop(eid, None)
            await self._on_expire(entity, eid, is_player)

    async def _do_effect_tick(self, entity, eid: str, se: StatusEffect, is_player: bool):
        """Dispatch per-effect tick logic."""
        cat = self._defs.get(eid, {}).get("category", "")
        if eid in ("bleeding", "major_bleed"):
            await self._tick_bleed(entity, se, is_player, major=(eid == "major_bleed"))
        elif eid in ("poisoned", "major_poison"):
            await self._tick_poison(entity, se, is_player, major=(eid == "major_poison"))
        elif eid == "disease":
            await self._tick_disease(entity, se, is_player)
        elif eid == "mind_rot":
            await self._tick_mind_rot(entity, se, is_player)
        elif cat == "DEBUFF_CONTROL" and eid in ("fear", "terrified", "horrified", "sheer_fear"):
            await self._tick_fear(entity, se, is_player, eid)
        elif eid == "prone":
            await self._tick_prone(entity, se, is_player)
        elif eid == "confused":
            await self._tick_confused(entity, se, is_player)
        elif eid == "frenzied":
            await self._tick_frenzied(entity, se, is_player)
        elif eid == "webbed":
            await self._tick_webbed(entity, se, is_player)
        elif eid == "floofer_glow":
            await self._tick_floofer_glow(entity, se, is_player)

    # ── DOT ticks ─────────────────────────────────────────────────────────────

    async def _tick_bleed(self, entity, se: StatusEffect, is_player: bool, major: bool):
        import random
        from server.core.protocol.colors import colorize, TextPresets

        if is_player:
            wb = getattr(self._server, "wound_bridge", None)
            if wb and getattr(entity, "character_id", None):
                try:
                    if not wb.is_bleeding(entity):
                        se.expires = 0
                        wb.sync_session_state(entity)
                        return
                except Exception:
                    pass

        if major:
            # Major bleed: percentage of remaining health
            damage = max(1, int((entity.health_current or 0) * 0.05 * se.stacks))
        else:
            damage = se.stacks * se.magnitude + random.randint(1, 3)
            damage = int(damage)

        if is_player:
            entity.health_current = max(0, entity.health_current - damage)
            await entity.send_line(colorize(
                f"  Your wound bleeds for {damage} hit points of damage!",
                TextPresets.COMBAT_DAMAGE_TAKEN
            ))
            # Natural clot chance
            if random.random() < (0.10 if major else 0.15):
                se.stacks = max(0, se.stacks - 1)
                if se.stacks == 0:
                    se.expires = 0
                    await entity.send_line(colorize(
                        "  Your bleeding slows and stops.",
                        TextPresets.SYSTEM
                    ))
            if entity.health_current <= 0:
                await entity.send_line(colorize("  You have bled to death!", TextPresets.COMBAT_DEATH))
                if hasattr(self._server, "combat"):
                    await self._server.combat._player_death(entity, None)
            elif self._server.db and entity.character_id:
                self._server.db.save_character_resources(
                    entity.character_id,
                    entity.health_current, entity.mana_current,
                    entity.spirit_current, entity.stamina_current,
                    entity.silver
                )
        else:
            entity.health_current = max(0, entity.health_current - damage)
            await self._server.world.broadcast_to_room(
                entity.current_room_id,
                colorize(f"  {entity.full_name.capitalize()} bleeds for {damage} damage!", TextPresets.COMBAT_DAMAGE_TAKEN)
            )
            if random.random() < 0.10:
                se.stacks = max(0, se.stacks - 1)
                if se.stacks == 0:
                    se.expires = 0
            if entity.health_current <= 0:
                await self._creature_dot_death(entity, "bleed")
            elif entity.health_current < entity.health_max * 0.20:
                if self.has(entity, "fear") or random.random() < 0.35:
                    await self._creature_flee(entity)

    async def _tick_poison(self, entity, se: StatusEffect, is_player: bool, major: bool):
        import random
        from server.core.protocol.colors import colorize, TextPresets

        if major:
            # Major poison: percentage of remaining health, stacks-based
            damage = max(1, int((entity.health_current or 0) * 0.04 * se.stacks))
        else:
            # Standard GS4: magnitude dissipates by 5 per tick
            damage = int(se.magnitude)
            se.magnitude = max(0, se.magnitude - 5)
            if se.magnitude <= 0:
                se.expires = 0  # fully dissipated

        if is_player:
            entity.health_current = max(0, entity.health_current - damage)
            await entity.send_line(colorize(
                f"  The poison courses through you for {damage} hit points!",
                TextPresets.COMBAT_DAMAGE_TAKEN
            ))
            if entity.health_current <= 0:
                await entity.send_line(colorize("  The poison claims your life!", TextPresets.COMBAT_DEATH))
                if hasattr(self._server, "combat"):
                    await self._server.combat._player_death(entity, None)
            elif self._server.db and entity.character_id:
                self._server.db.save_character_resources(
                    entity.character_id,
                    entity.health_current, entity.mana_current,
                    entity.spirit_current, entity.stamina_current,
                    entity.silver
                )
        else:
            entity.health_current = max(0, entity.health_current - damage)
            await self._server.world.broadcast_to_room(
                entity.current_room_id,
                colorize(f"  {entity.full_name.capitalize()} shudders as poison ravages its body!", TextPresets.COMBAT_DAMAGE_TAKEN)
            )
            if entity.health_current <= 0:
                await self._creature_dot_death(entity, "poison")
            elif entity.health_current < entity.health_max * 0.15:
                if random.random() < 0.40:
                    await self._creature_flee(entity)

    async def _tick_disease(self, entity, se: StatusEffect, is_player: bool):
        import random
        from server.core.protocol.colors import colorize, TextPresets
        damage = int(se.magnitude) + random.randint(0, 2)
        if is_player:
            entity.health_current = max(0, entity.health_current - damage)
            await entity.send_line(colorize(
                f"  The disease weakens you for {damage} damage!",
                TextPresets.COMBAT_DAMAGE_TAKEN
            ))

    async def _tick_mind_rot(self, entity, se: StatusEffect, is_player: bool):
        import random
        from server.core.protocol.colors import colorize, TextPresets
        damage = int(se.magnitude) + random.randint(0, 1)
        if is_player:
            entity.spirit_current = max(0, entity.spirit_current - damage)
            await entity.send_line(colorize(
                f"  Mind rot eats at your spirit for {damage} points!",
                TextPresets.COMBAT_DAMAGE_TAKEN
            ))
            if entity.spirit_current <= 0:
                await entity.send_line(colorize("  The mind rot consumes your spirit!", TextPresets.COMBAT_DEATH))
                if hasattr(self._server, "combat"):
                    await self._server.combat._player_death(entity, None)

    # ── Behavioral ticks ─────────────────────────────────────────────────────

    async def _tick_fear(self, entity, se: StatusEffect, is_player: bool, eid: str):
        import random
        flee_chance = {"fear": 0.25, "terrified": 0.50, "horrified": 0.40, "sheer_fear": 0.0}.get(eid, 0.25)
        if not is_player and entity.in_combat and flee_chance > 0:
            if random.random() < flee_chance:
                await self._creature_flee(entity)

    async def _tick_prone(self, entity, se: StatusEffect, is_player: bool):
        import random
        from server.core.protocol.colors import colorize, TextPresets
        # 40% chance per tick to stand up on own
        if random.random() < 0.40:
            se.expires = 0
            if is_player:
                entity.position = "standing"
                self.remove(entity, "prone")
                await entity.send_line(colorize("  You scramble back to your feet.", TextPresets.SYSTEM))
            else:
                await self._server.world.broadcast_to_room(
                    entity.current_room_id,
                    colorize(f"  {entity.full_name.capitalize()} struggles back to its feet.", TextPresets.SYSTEM)
                )

    async def _tick_confused(self, entity, se: StatusEffect, is_player: bool):
        """Confused creatures/players may attack a random target."""
        import random
        if not is_player:
            return  # creature confusion handled by combat engine
        # For players: just a cosmetic message while confused
        from server.core.protocol.colors import colorize, TextPresets
        msgs = [
            "  Your mind swims in confusion.",
            "  You struggle to focus through the confusion.",
        ]
        await entity.send_line(colorize(random.choice(msgs), TextPresets.SYSTEM))

    async def _tick_frenzied(self, entity, se: StatusEffect, is_player: bool):
        """Frenzied: deal minor uncontrolled damage to surroundings."""
        pass  # Handled in combat engine; tick just holds the status

    async def _tick_webbed(self, entity, se: StatusEffect, is_player: bool):
        """Webbed: chance to break free each tick."""
        import random
        if is_player and random.random() < 0.10:
            se.expires = 0  # will expire next cleanup

    async def _tick_floofer_glow(self, entity, se: StatusEffect, is_player: bool):
        """Silent pet-driven regeneration that stacks with other regen sources, but not itself."""
        if not is_player:
            return
        if getattr(entity, "is_dead", False):
            return

        heal_pct = float(se.data.get("heal_pct", se.magnitude or 0.01))
        if heal_pct <= 0:
            return

        health_max = int(getattr(entity, "health_max", 0) or 0)
        current_hp = int(getattr(entity, "health_current", 0) or 0)
        if health_max <= 0 or current_hp >= health_max:
            return

        heal_amount = max(1, int(health_max * heal_pct))
        entity.health_current = min(health_max, current_hp + heal_amount)

        if self._server.db and getattr(entity, "character_id", None):
            self._server.db.save_character_resources(
                entity.character_id,
                entity.health_current,
                entity.mana_current,
                entity.spirit_current,
                entity.stamina_current,
                entity.silver,
            )

    # ── Effect expiry ─────────────────────────────────────────────────────────

    async def _on_expire(self, entity, eid: str, is_player: bool):
        """Called when an effect's timer runs out."""
        from server.core.protocol.colors import colorize, TextPresets

        # Sync booleans/position on expiry
        self._sync_entity_flags(entity, eid, False)

        # in_combat expiry: check if still being attacked before clearing
        if eid == "in_combat":
            await self._handle_combat_expire(entity, is_player)
            return

        if not is_player:
            return

        msg = _EXPIRE_MESSAGES.get(eid)
        if msg:
            await entity.send_line(colorize(msg, TextPresets.SYSTEM))

        # Special post-expiry effects
        if eid == "bleeding" or eid == "major_bleed":
            await entity.send_line(colorize("  Your bleeding has stopped.", TextPresets.SYSTEM))
        elif eid == "prone":
            entity.position = "standing"

    async def _handle_combat_expire(self, entity, is_player: bool):
        """
        Called when the in_combat status expires (8 seconds after last hit).
        Re-applies if hostile creatures in room are still targeting the player.
        Otherwise fully clears combat and sends the area-clear message.
        """
        from server.core.protocol.colors import colorize, TextPresets

        if not is_player:
            entity.in_combat = False
            entity.target    = None
            return

        # Check for alive hostile creatures in the room still targeting this player
        room    = getattr(entity, "current_room", None)
        room_id = room.id if room else getattr(entity, "current_room_id", None)

        still_engaged = False
        if room_id and hasattr(self._server, "creatures"):
            for c in self._server.creatures.get_creatures_in_room(room_id):
                if c.alive and getattr(c, "in_combat", False) and c.target is entity:
                    still_engaged = True
                    break

        if still_engaged:
            # Re-apply combat — something is still actively attacking us
            self.apply(entity, "in_combat", duration=8, source=entity.target)
        else:
            # Truly clear
            entity.in_combat = False
            entity.target    = None
            self.apply(entity, "exited_combat", duration=3)
            await entity.send_line(colorize(
                "The combat area is clear.",
                TextPresets.SYSTEM
            ))

    # ── Backward compat flag sync ─────────────────────────────────────────────

    def _sync_entity_flags(self, entity, eid: str, applied: bool):
        """Keep session.position and session.in_combat in sync."""
        pos_map = {
            "sleeping":  "sleeping",
            "resting":   "sitting",
            "sitting":   "sitting",
            "kneeling":  "kneeling",
            "prone":     "lying",
        }
        if eid == "in_combat":
            if not applied:
                entity.in_combat = False
                entity.target    = None
        elif eid in pos_map and hasattr(entity, "position"):
            if applied:
                entity.position = pos_map[eid]
            else:
                # Only reset to standing if no other position effects active
                other_pos = [k for k in pos_map if k != eid and self.has(entity, k)]
                if not other_pos:
                    entity.position = "standing"

    # ── Creature helpers ──────────────────────────────────────────────────────

    async def _creature_flee(self, creature):
        """Creature flees to a random adjacent non-safe room."""
        import random
        from server.core.protocol.colors import colorize, TextPresets

        room = self._server.world.get_room(creature.current_room_id)
        if not room or not room.exits:
            return

        valid_exits = [
            (d, rid) for d, rid in room.exits.items()
            if not d.startswith("go_")
            and not getattr(self._server.world.get_room(rid), "safe", False)
        ]
        if not valid_exits:
            return

        direction, new_room_id = random.choice(valid_exits)
        flee_msgs = [
            f"{creature.full_name.capitalize()} panics and flees {direction}!",
            f"{creature.full_name.capitalize()} turns and runs {direction} in terror!",
            f"{creature.full_name.capitalize()} breaks away and flees {direction}!",
        ]
        await self._server.world.broadcast_to_room(
            creature.current_room_id,
            colorize(random.choice(flee_msgs), TextPresets.CREATURE_NAME)
        )

        # Clean combat on both sides
        if creature.target:
            self.exit_combat(creature.target)
            if hasattr(creature.target, "send_line"):
                await creature.target.send_line(colorize(
                    f"  {creature.full_name.capitalize()} flees!", TextPresets.SYSTEM
                ))
        creature.in_combat = False
        creature.target    = None

        # Move creature
        old_id = creature.current_room_id
        if old_id in self._server.creatures._room_creatures:
            try:
                self._server.creatures._room_creatures[old_id].remove(creature.id)
            except ValueError:
                pass

        creature.current_room_id = new_room_id
        self._server.creatures._room_creatures.setdefault(new_room_id, []).append(creature.id)

        await self._server.world.broadcast_to_room(
            new_room_id,
            colorize(f"{creature.full_name.capitalize()} staggers in, badly wounded!", TextPresets.CREATURE_NAME)
        )

    async def _creature_dot_death(self, creature, cause: str):
        """Creature dies from a DOT effect."""
        import random
        from server.core.protocol.colors import colorize, TextPresets

        creature.status_effects = {}
        msgs = {
            "bleed":  [
                f"  {creature.full_name.capitalize()} collapses and dies from blood loss!",
                f"  {creature.full_name.capitalize()} shudders and falls dead, its wounds too great!",
            ],
            "poison": [
                f"  {creature.full_name.capitalize()} convulses and dies from the poison!",
                f"  {creature.full_name.capitalize()} lets out a final cry and dies from poisoning!",
            ],
        }
        msg = random.choice(msgs.get(cause, [f"  {creature.full_name.capitalize()} dies!"]))
        await self._server.world.broadcast_to_room(
            creature.current_room_id,
            colorize(msg, TextPresets.CREATURE_NAME)
        )
        self._server.creatures.mark_dead(creature)
        attacker = getattr(creature, "last_attacker", None)
        if attacker and hasattr(self._server, "experience"):
            from server.core.commands.player.party import award_party_kill_xp
            await award_party_kill_xp(attacker, creature, self._server)
