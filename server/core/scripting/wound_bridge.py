"""
wound_bridge.py
---------------
Python <-> Lua bridge for the GemStone IV wound/treatment system.

All wound LOGIC lives in Lua (wound_system.lua, treatment.lua,
bleed_system.lua, herbs.lua).  This module is a thin adapter that:

  1. Converts session.wounds (Python dict) -> Lua table and back
  2. Calls Lua functions and returns plain Python results
  3. Loads/saves wounds from/to the MySQL character_wounds table
  4. Exposes a clean Python API so combat_engine, actions, etc.
     never need to know Lua exists

Usage
-----
    from server.core.scripting.wound_bridge import WoundBridge

    # One WoundBridge per server; pass server reference for DB + LuaEngine
    bridge = WoundBridge(server)
    await bridge.initialize()           # loads Lua modules

    # Combat hit applies wound
    result = bridge.apply_wound(session, location, crit_rank)

    # Player tends a wound
    result = bridge.tend(session, location_input)

    # Player eats an herb
    result = bridge.use_herb(session, item_dict)

    # Game-loop bleed tick
    result = bridge.bleed_tick(session)

    # Load wounds from DB on login
    await bridge.load_wounds(session)

    # Save wounds to DB (call after any change)
    await bridge.save_wounds(session)
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


class WoundBridge:
    """Thin adapter between Python session data and the Lua wound system."""

    def __init__(self, server):
        self._server = server
        self._lua_engine = None
        self._wound_sys   = None  # Lua WoundSystem table
        self._treatment   = None  # Lua Treatment table
        self._bleed_sys   = None  # Lua BleedSystem table
        self._herbs       = None  # Lua Herbs table

    # ──────────────────────────────────────────────────────────────────
    # Initialisation
    # ──────────────────────────────────────────────────────────────────

    async def initialize(self):
        """Load Lua wound modules.  Safe to call even if Lua is unavailable."""
        try:
            lua_mgr = getattr(self._server, 'lua', None)
            if not lua_mgr or not lua_mgr.engine or not lua_mgr.engine.available:
                log.warning("WoundBridge: Lua unavailable — wound system disabled")
                return

            self._lua_engine = lua_mgr.engine
            rt = self._lua_engine._lua

            self._wound_sys  = rt.eval("require('globals/wound_system')")
            self._treatment  = rt.eval("require('globals/treatment')")
            self._bleed_sys  = rt.eval("require('globals/bleed_system')")
            self._herbs      = rt.eval("require('globals/herbs')")
            log.info("WoundBridge: Lua wound modules loaded")

        except Exception as e:
            log.error("WoundBridge: initialization failed: %s", e, exc_info=True)

    @property
    def available(self) -> bool:
        return self._wound_sys is not None

    # ──────────────────────────────────────────────────────────────────
    # Dict <-> Lua table conversion
    # ──────────────────────────────────────────────────────────────────

    def _wounds_to_lua(self, wounds_dict: dict):
        """Convert Python wounds dict to a Lua table."""
        if not self._lua_engine:
            return None
        # LuaEngine exposes the runtime as _lua (a lupa LuaRuntime).
        # Use rt.eval("{}") to create Lua tables — lupa has no rt.table() method.
        rt = self._lua_engine._lua

        lua_tbl = rt.eval("{}")
        for loc, entry in (wounds_dict or {}).items():
            e = rt.eval("{}")
            e['wound_rank']  = int(entry.get('wound_rank',  0))
            e['scar_rank']   = int(entry.get('scar_rank',   0))
            e['is_bleeding'] = bool(entry.get('is_bleeding', False))
            e['bandaged']    = bool(entry.get('bandaged',    False))
            lua_tbl[loc] = e
        return lua_tbl

    def _lua_to_wounds(self, lua_tbl) -> dict:
        """Convert a Lua wounds table back to a Python dict."""
        if lua_tbl is None:
            return {}
        from server.core.scripting.lua_engine import lua_to_python
        raw = lua_to_python(lua_tbl)
        if not isinstance(raw, dict):
            return {}
        result = {}
        for loc, entry in raw.items():
            if isinstance(entry, dict):
                result[str(loc)] = {
                    'wound_rank':  int(entry.get('wound_rank',  0)),
                    'scar_rank':   int(entry.get('scar_rank',   0)),
                    'is_bleeding': bool(entry.get('is_bleeding', False)),
                    'bandaged':    bool(entry.get('bandaged',    False)),
                }
        return result

    def _lua_result_to_py(self, lua_tbl) -> dict:
        """Convert a Lua result table to a Python dict."""
        from server.core.scripting.lua_engine import lua_to_python
        raw = lua_to_python(lua_tbl)
        return raw if isinstance(raw, dict) else {}

    # ──────────────────────────────────────────────────────────────────
    # Session wound accessors
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_wounds(session) -> dict:
        """Return session.wounds, initialising to empty dict if absent."""
        if not hasattr(session, 'wounds') or session.wounds is None:
            session.wounds = {}
        return session.wounds

    @staticmethod
    def _set_wounds(session, wounds_dict: dict):
        session.wounds = wounds_dict

    def sync_session_state(self, session):
        """Mirror canonical wound data into legacy injury/status state."""
        wounds = self.get_wounds(session)

        injuries = {}
        bleeding_locs = []
        highest_bleed_rank = 0
        for loc, entry in wounds.items():
            if not isinstance(entry, dict):
                continue
            wr = int(entry.get('wound_rank', 0) or 0)
            if wr > 0:
                injuries[loc] = wr
            if entry.get('is_bleeding') and not entry.get('bandaged'):
                bleeding_locs.append(loc)
                highest_bleed_rank = max(highest_bleed_rank, wr)
        session.injuries = injuries

        status_mgr = getattr(self._server, 'status', None)
        if status_mgr:
            status_mgr.remove(session, 'bleeding')
            status_mgr.remove(session, 'major_bleed')
            status_mgr.remove(session, 'wounded')

            if injuries:
                status_mgr.apply(session, 'wounded', duration=300, stacks=1)
            if bleeding_locs:
                effect_id = 'major_bleed' if highest_bleed_rank >= 3 or len(bleeding_locs) >= 3 else 'bleeding'
                stacks = min(5, max(1, len(bleeding_locs)))
                magnitude = max(1, highest_bleed_rank)
                status_mgr.apply(session, effect_id, duration=90, stacks=stacks, magnitude=magnitude)
            return

        effects = getattr(session, 'status_effects', {}) or {}
        effects.pop('bleed', None)
        effects.pop('bleeding', None)
        effects.pop('major_bleed', None)
        effects.pop('wounded', None)
        if injuries:
            effects['wounded'] = {'active': True}
        if bleeding_locs:
            effects['bleeding'] = {
                'active': True,
                'stacks': min(5, max(1, len(bleeding_locs))),
                'magnitude': max(1, highest_bleed_rank),
            }
        session.status_effects = effects

    # ──────────────────────────────────────────────────────────────────
    # Core wound operations
    # ──────────────────────────────────────────────────────────────────

    def apply_wound(self, session, location: str, crit_rank: int) -> dict:
        """
        Apply a wound from combat at the given location and crit rank.
        Returns dict: { new_rank, did_bleed, message }
        Falls back to a safe Python path if Lua is unavailable.
        """
        wounds = self.get_wounds(session)

        if not self.available:
            return self._fallback_apply_wound(wounds, location, crit_rank)

        try:
            lua_wounds = self._wounds_to_lua(wounds)
            result = self._wound_sys.apply_wound(lua_wounds, location, crit_rank)
            # result = (new_rank, did_bleed, msg, updated_entry) in Lua
            # lupa returns multiple returns as a tuple
            if isinstance(result, tuple):
                new_rank, did_bleed, msg, updated_entry = result
            else:
                # Single return (no wound assigned at this crit rank)
                new_rank = int(result) if result else 0
                did_bleed = False
                msg = None
                updated_entry = None

            new_rank  = int(new_rank) if new_rank else 0
            did_bleed = bool(did_bleed)

            if new_rank > 0 and updated_entry is not None:
                from server.core.scripting.lua_engine import lua_to_python
                entry = lua_to_python(updated_entry)
                if isinstance(entry, dict):
                    wounds[location] = {
                        'wound_rank':  int(entry.get('wound_rank',  new_rank)),
                        'scar_rank':   int(entry.get('scar_rank',   0)),
                        'is_bleeding': bool(entry.get('is_bleeding', did_bleed)),
                        'bandaged':    bool(entry.get('bandaged',    False)),
                    }
                self._set_wounds(session, wounds)
                self.sync_session_state(session)

            return {
                'new_rank':  new_rank,
                'did_bleed': did_bleed,
                'message':   str(msg) if msg else None,
            }

        except Exception as e:
            log.error("WoundBridge.apply_wound error: %s", e, exc_info=True)
            return self._fallback_apply_wound(wounds, location, crit_rank)

    def _fallback_apply_wound(self, wounds: dict, location: str, crit_rank: int) -> dict:
        """Pure Python fallback if Lua is down."""
        CRIT_TO_RANK = {1:0,2:0,3:1,4:1,5:2,6:2,7:3,8:3,9:3}
        new_rank  = CRIT_TO_RANK.get(crit_rank, 0)
        did_bleed = crit_rank >= 5

        if new_rank > 0:
            existing = wounds.get(location, {})
            final    = max(existing.get('wound_rank', 0), new_rank)
            wounds[location] = {
                'wound_rank':  final,
                'scar_rank':   existing.get('scar_rank', 0),
                'is_bleeding': did_bleed or existing.get('is_bleeding', False),
                'bandaged':    False if did_bleed else existing.get('bandaged', False),
            }

        return {'new_rank': new_rank, 'did_bleed': did_bleed, 'message': None}

    # ──────────────────────────────────────────────────────────────────

    def tend(self, session, location_input: str) -> dict:
        """
        TEND a bleeding wound at the given location.
        Does NOT reduce wound rank — only stops bleeding.
        Returns dict: { ok, message }
        """
        wounds  = self.get_wounds(session)
        fa_bonus = self._get_fa_bonus(session)

        if not self.available:
            return {'ok': False,
                    'message': "You attempt to tend the wound. (Lua unavailable)"}

        try:
            lua_wounds = self._wounds_to_lua(wounds)
            lua_result = self._treatment.tend(lua_wounds, location_input, fa_bonus)
            res        = self._lua_result_to_py(lua_result)

            if res.get('ok'):
                updated = self._lua_to_wounds(lua_result['wounds'] if hasattr(lua_result, '__getitem__') else lua_wounds)
                self._set_wounds(session, updated)
                self.sync_session_state(session)

            return {'ok': bool(res.get('ok')), 'message': str(res.get('msg', ''))}

        except Exception as e:
            log.error("WoundBridge.tend error: %s", e, exc_info=True)
            return {'ok': False, 'message': "You fumble with the bandages."}

    # ──────────────────────────────────────────────────────────────────

    def use_herb(self, session, item_dict: dict) -> dict:
        """
        Apply an herb from inventory to the player's wounds.
        Returns dict: { ok, message, hp_restore, mana_restore, cure_poison }
        """
        wounds   = self.get_wounds(session)
        fa_bonus = self._get_fa_bonus(session)

        if not self.available:
            return {'ok': False, 'message': "The herb has no effect. (Lua unavailable)",
                    'hp_restore': 0, 'mana_restore': 0, 'cure_poison': False}

        try:
            # Find herb data from Lua herb table
            noun = (item_dict.get('noun') or item_dict.get('name') or '').lower()
            noun_key = noun.replace(' ', '_').replace('-', '_')
            herb_data = self._herbs.find_by_noun(noun_key)

            if herb_data is None:
                # Try DB heal_type field as fallback
                return self._fallback_herb(session, wounds, item_dict)

            lua_wounds = self._wounds_to_lua(wounds)
            lua_result = self._treatment.use_herb(lua_wounds, herb_data, fa_bonus)
            res        = self._lua_result_to_py(lua_result)

            if res.get('ok'):
                # Update wounds dict from Lua result
                try:
                    updated = self._lua_to_wounds(lua_result['wounds'])
                    self._set_wounds(session, updated)
                    self.sync_session_state(session)
                except Exception:
                    pass

            return {
                'ok':          bool(res.get('ok', False)),
                'message':     str(res.get('msg', '')),
                'hp_restore':  int(res.get('hp_restore', 0) or 0),
                'mana_restore': int(res.get('mana_restore', 0) or 0),
                'cure_poison': bool(res.get('cure_poison', False)),
                'scar_added':  bool(res.get('scar_added', False)),
            }

        except Exception as e:
            log.error("WoundBridge.use_herb error: %s", e, exc_info=True)
            return self._fallback_herb(session, wounds, item_dict)

    def _fallback_herb(self, session, wounds: dict, item_dict: dict) -> dict:
        """Fallback herb handler using raw DB item fields."""
        heal_type   = item_dict.get('heal_type') or item_dict.get('herb_heal_type') or 'blood'
        heal_amount = int(item_dict.get('heal_amount') or item_dict.get('herb_heal_amount') or 0)
        msg = "You feel the herb working."
        hp_restore = heal_amount if heal_type in ('blood', 'health') else 0
        return {
            'ok': True, 'message': msg,
            'hp_restore': hp_restore, 'mana_restore': 0,
            'cure_poison': heal_type == 'poison', 'scar_added': False,
        }

    # ──────────────────────────────────────────────────────────────────

    def bleed_tick(self, session) -> dict:
        """
        Process one bleed tick for the session.
        Returns dict: { damage, messages }
        Call from game loop every ~8 seconds for bleeding characters.
        """
        wounds = self.get_wounds(session)
        if not wounds:
            return {'damage': 0, 'messages': []}

        if not self.available:
            return {'damage': 0, 'messages': []}

        try:
            lua_wounds = self._wounds_to_lua(wounds)
            damage, messages, updated_wounds = self._bleed_sys.tick(lua_wounds)

            damage = int(damage) if damage else 0

            msgs = []
            if messages:
                from server.core.scripting.lua_engine import lua_to_python
                raw = lua_to_python(messages)
                if isinstance(raw, list):
                    msgs = [str(m) for m in raw]
                elif isinstance(raw, str):
                    msgs = [raw]

            # Check for natural bleed stop
            try:
                stopped, updated_wounds2 = self._bleed_sys.check_natural_stop(lua_wounds)
                from server.core.scripting.lua_engine import lua_to_python
                stopped_list = lua_to_python(stopped)
                if isinstance(stopped_list, list) and stopped_list:
                    stop_locs = ', '.join(str(s) for s in stopped_list)
                    msgs.append(f"The bleeding from your {stop_locs} has slowed and stopped.")
                updated_wounds = updated_wounds2
            except Exception:
                pass

            # Sync back to Python
            updated_py = self._lua_to_wounds(updated_wounds)
            if updated_py:
                self._set_wounds(session, updated_py)
                self.sync_session_state(session)

            return {'damage': damage, 'messages': msgs}

        except Exception as e:
            log.error("WoundBridge.bleed_tick error: %s", e, exc_info=True)
            return {'damage': 0, 'messages': []}

    # ──────────────────────────────────────────────────────────────────

    def blocks_cast(self, session) -> tuple:
        """Returns (blocked: bool, location: str|None)"""
        return self._check_ability(session, 'blocks_cast')

    def blocks_search(self, session) -> tuple:
        return self._check_ability(session, 'blocks_search')

    def blocks_sneak(self, session) -> tuple:
        return self._check_ability(session, 'blocks_sneak')

    def blocks_ranged(self, session) -> tuple:
        return self._check_ability(session, 'blocks_ranged')

    def _check_ability(self, session, fn_name: str) -> tuple:
        if not self.available:
            return False, None
        try:
            wounds    = self.get_wounds(session)
            lua_wounds = self._wounds_to_lua(wounds)
            fn        = getattr(self._wound_sys, fn_name)
            result    = fn(lua_wounds)
            if isinstance(result, tuple):
                blocked, loc = result
                return bool(blocked), str(loc) if loc else None
            return bool(result), None
        except Exception as e:
            log.debug("WoundBridge.%s error: %s", fn_name, e)
            return False, None

    def as_penalty(self, session) -> int:
        """Total AS penalty from all active wounds/scars."""
        return self._stat_penalty(session, 'as_penalty')

    def ds_penalty(self, session) -> int:
        return self._stat_penalty(session, 'ds_penalty')

    def _stat_penalty(self, session, fn_name: str) -> int:
        if not self.available:
            return 0
        try:
            wounds    = self.get_wounds(session)
            lua_wounds = self._wounds_to_lua(wounds)
            fn        = getattr(self._wound_sys, fn_name)
            return int(fn(lua_wounds) or 0)
        except Exception:
            return 0

    # ──────────────────────────────────────────────────────────────────

    def get_health_display(self, session) -> list:
        """
        Returns a list of dicts for the HEALTH command wound section.
        Each dict: { type, location, rank, desc, suffix }
        """
        wounds = self.get_wounds(session)
        if not wounds:
            return [{'type': 'none', 'desc': 'None'}]

        if not self.available:
            return self._fallback_health_display(wounds)

        try:
            lua_wounds = self._wounds_to_lua(wounds)
            lua_lines  = self._wound_sys.health_display(lua_wounds)
            from server.core.scripting.lua_engine import lua_to_python
            lines = lua_to_python(lua_lines)
            if isinstance(lines, list):
                out = []
                for item in lines:
                    if isinstance(item, dict):
                        out.append({
                            'type':     str(item.get('type', 'wound')),
                            'location': str(item.get('location', '')),
                            'rank':     int(item.get('rank', 0) or 0),
                            'desc':     str(item.get('desc', '')),
                            'suffix':   str(item.get('suffix', '')),
                        })
                return out or [{'type': 'none', 'desc': 'None'}]
        except Exception as e:
            log.debug("WoundBridge.get_health_display error: %s", e)

        return self._fallback_health_display(wounds)

    def _fallback_health_display(self, wounds: dict) -> list:
        SEV = {1:'minor', 2:'moderate', 3:'severe'}
        lines = []
        for loc, entry in sorted(wounds.items()):
            wr = entry.get('wound_rank', 0)
            sr = entry.get('scar_rank',  0)
            if wr > 0:
                bleed = '  [BLEEDING]' if entry.get('is_bleeding') and not entry.get('bandaged') else \
                        '  [bandaged]' if entry.get('bandaged') else ''
                lines.append({
                    'type': 'wound', 'location': loc.replace('_', ' '),
                    'rank': wr,
                    'desc': f"{SEV.get(wr, 'unknown')} wound",
                    'suffix': bleed,
                })
            elif sr > 0:
                lines.append({
                    'type': 'scar', 'location': loc.replace('_', ' '),
                    'rank': sr,
                    'desc': f"rank {sr} scar",
                    'suffix': '',
                })
        return lines or [{'type': 'none', 'desc': 'None'}]

    # ──────────────────────────────────────────────────────────────────

    def empath_heal(self, empath_session, target_session, location_input: str = None) -> dict:
        """
        Empath TRANSFER + heal.  If location_input is None, heals all.
        """
        target_wounds = self.get_wounds(target_session)

        if not self.available:
            return {'ok': False, 'message': "Healing unavailable."}

        try:
            lua_target = self._wounds_to_lua(target_wounds)

            if location_input:
                lua_result = self._treatment.empath_heal(lua_target, location_input)
            else:
                lua_result = self._treatment.empath_heal_all(lua_target)

            res = self._lua_result_to_py(lua_result)

            if res.get('ok'):
                try:
                    updated = self._lua_to_wounds(lua_result['wounds'])
                    self._set_wounds(target_session, updated)
                    self.sync_session_state(target_session)
                except Exception:
                    pass

            return {'ok': bool(res.get('ok')), 'message': str(res.get('msg', ''))}

        except Exception as e:
            log.error("WoundBridge.empath_heal error: %s", e, exc_info=True)
            return {'ok': False, 'message': "The healing fails."}

    # ──────────────────────────────────────────────────────────────────
    # DB persistence
    # ──────────────────────────────────────────────────────────────────

    async def load_wounds(self, session):
        """Load wounds from DB into session.wounds on character login."""
        char_id = getattr(session, 'character_id', None)
        if not char_id or not self._server.db:
            session.wounds = {}
            return

        try:
            db   = self._server.db
            rows = db.execute_query(
                "SELECT location, wound_rank, scar_rank, is_bleeding, bandaged "
                "FROM character_wounds WHERE character_id = %s",
                (char_id,)
            )
            wounds = {}
            for row in (rows or []):
                loc = row.get('location') or row[0]
                wounds[loc] = {
                    'wound_rank':  int(row.get('wound_rank',  row[1])),
                    'scar_rank':   int(row.get('scar_rank',   row[2])),
                    'is_bleeding': bool(row.get('is_bleeding', row[3])),
                    'bandaged':    bool(row.get('bandaged',    row[4])),
                }
            session.wounds = wounds
            self.sync_session_state(session)
            if wounds:
                log.debug("WoundBridge: loaded %d wound records for char %d",
                          len(wounds), char_id)
        except Exception as e:
            log.error("WoundBridge.load_wounds: %s", e, exc_info=True)
            session.wounds = {}

    async def save_wounds(self, session):
        """Persist session.wounds to DB.  Uses UPSERT for efficiency."""
        char_id = getattr(session, 'character_id', None)
        wounds  = getattr(session, 'wounds', {}) or {}
        if not char_id or not self._server.db:
            return

        try:
            db = self._server.db

            # Delete cleared locations (wound_rank=0 AND scar_rank=0)
            for loc, entry in list(wounds.items()):
                if entry.get('wound_rank', 0) == 0 and entry.get('scar_rank', 0) == 0:
                    db.execute_query(
                        "DELETE FROM character_wounds "
                        "WHERE character_id=%s AND location=%s",
                        (char_id, loc)
                    )

            # Upsert active entries
            for loc, entry in wounds.items():
                wr = entry.get('wound_rank', 0)
                sr = entry.get('scar_rank',  0)
                if wr > 0 or sr > 0:
                    db.execute_query(
                        """
                        INSERT INTO character_wounds
                            (character_id, location, wound_rank, scar_rank, is_bleeding, bandaged)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            wound_rank  = VALUES(wound_rank),
                            scar_rank   = VALUES(scar_rank),
                            is_bleeding = VALUES(is_bleeding),
                            bandaged    = VALUES(bandaged)
                        """,
                        (
                            char_id, loc, wr, sr,
                            1 if entry.get('is_bleeding') else 0,
                            1 if entry.get('bandaged')    else 0,
                        )
                    )
        except Exception as e:
            log.error("WoundBridge.save_wounds: %s", e, exc_info=True)

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_fa_bonus(session) -> int:
        """Get First Aid skill bonus (ranks * 3). Skill ID 30."""
        SKILL_FIRST_AID = 30
        skills = getattr(session, 'skills', {}) or {}
        fa = skills.get(SKILL_FIRST_AID, {})
        if isinstance(fa, dict):
            bonus = int(fa.get('bonus', 0))
            return bonus if bonus else int(fa.get('ranks', 0)) * 3
        return 0

    def is_bleeding(self, session) -> bool:
        """Quick check: is the player bleeding from any location?"""
        wounds = self.get_wounds(session)
        return any(
            e.get('is_bleeding') and not e.get('bandaged')
            for e in wounds.values()
        )
