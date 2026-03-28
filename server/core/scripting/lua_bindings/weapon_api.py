"""
weapon_api.py
-------------
Python <-> Lua bridge for the Weapon Techniques system.

Responsibilities:
  1. Build entity snapshots from session objects for Lua consumption
  2. Receive Lua result tables and apply all side-effects:
       - Status effects via StatusManager
       - Stamina drain
       - Roundtime assignment
       - Reaction trigger tracking (session.reaction_triggers)
       - Standard attack roll resolution (for techniques that trigger one)
       - AoE target gathering from room
       - Deferred AoE scheduling (Volley)
  3. Expose creature_use_technique() for combat engine
  4. Expose set_reaction_trigger() / clear_reaction_trigger() for combat engine hooks

Called by:
  weapon_techniques.py (cmd_weapon) -> execute_technique(session, mnemonic, target_name, limb)
  combat_engine.py  -> set_reaction_trigger(), creature_use_technique()
"""

import asyncio
import logging
import time
from typing import Optional, List

from server.core.engine.combat.smr_engine import smr_roll, moc_hits, open_d100
from server.core.engine.combat.status_effects import (
    apply_effect, apply_stun, apply_prone, apply_stagger, apply_vulnerable,
    apply_crippled, apply_slowed,
)
from server.core.protocol.colors import colorize, TextPresets, roundtime_msg

log = logging.getLogger(__name__)

# Reaction trigger expiry in seconds (GS4: approximately 8 seconds)
REACTION_TRIGGER_TTL = 8.0


# ── Skill name normalization ──────────────────────────────────────────────────
# Maps technique weapon_category to session skill_ranks key
_CAT_TO_SKILL_KEY = {
    "brawling":  "brawling",
    "blunt":     "blunt_weapons",
    "edged":     "edged_weapons",
    "polearm":   "polearm_weapons",
    "ranged":    "ranged_weapons",
    "twohanded": "two_handed_weapons",
}


def _get_skill_ranks(session, skill_key: str) -> int:
    skills = getattr(session, 'skills', {}) or {}
    d = skills.get(skill_key) or skills.get(skill_key.replace('_', ' '))
    if isinstance(d, dict):
        return int(d.get('ranks', 0))
    return int(d or 0)


def _get_moc_ranks(session) -> int:
    return _get_skill_ranks(session, 'multi_opponent_combat')


# ── Reaction trigger tracking ─────────────────────────────────────────────────

def set_reaction_trigger(session, trigger_name: str):
    """
    Called by combat_engine when a parry/evade/block occurs.
    Sets the trigger on the session with an expiry timestamp.
    """
    if not hasattr(session, 'reaction_triggers') or session.reaction_triggers is None:
        session.reaction_triggers = {}
    session.reaction_triggers[trigger_name] = time.monotonic() + REACTION_TRIGGER_TTL
    log.debug("Reaction trigger set: %s -> session %s", trigger_name, getattr(session, 'character_id', '?'))


def clear_reaction_trigger(session, trigger_name: str):
    if hasattr(session, 'reaction_triggers') and session.reaction_triggers:
        session.reaction_triggers.pop(trigger_name, None)


def has_reaction_trigger(session, trigger_name: str) -> bool:
    """Check if trigger is set and not expired."""
    rt = getattr(session, 'reaction_triggers', {}) or {}
    if trigger_name == 'recent_evade_block_parry':
        for k in ('recent_evade', 'recent_block', 'recent_parry'):
            expiry = rt.get(k, 0)
            if time.monotonic() < expiry:
                return True
        return False
    expiry = rt.get(trigger_name, 0)
    return time.monotonic() < expiry


def _build_trigger_snapshot(session) -> dict:
    """Build a reaction_triggers dict for Lua (bools, not timestamps)."""
    rt = getattr(session, 'reaction_triggers', {}) or {}
    now = time.monotonic()
    return {k: now < v for k, v in rt.items()}


# ── Entity snapshot builders ──────────────────────────────────────────────────

def _session_to_entity(session) -> dict:
    """Build a Lua-compatible entity dict from a session."""
    skills = getattr(session, 'skills', {}) or {}

    def _ranks(key):
        d = skills.get(key) or skills.get(key.replace('_', ' ')) or {}
        return int(d.get('ranks', 0)) if isinstance(d, dict) else int(d or 0)

    stats = getattr(session, 'stats', {}) or {}

    return {
        'skill_ranks': {
            'dodging':              _ranks('dodging'),
            'combat_maneuvers':     _ranks('combat_maneuvers'),
            'perception':           _ranks('perception'),
            'physical_fitness':     _ranks('physical_fitness'),
            'shield_use':           _ranks('shield_use'),
            'brawling':             _ranks('brawling'),
            'blunt_weapons':        _ranks('blunt_weapons'),
            'edged_weapons':        _ranks('edged_weapons'),
            'polearm_weapons':      _ranks('polearm_weapons'),
            'ranged_weapons':       _ranks('ranged_weapons'),
            'two_handed_weapons':   _ranks('two_handed_weapons'),
            'multi_opponent_combat': _ranks('multi_opponent_combat'),
        },
        'stats': {
            'agility':   int(stats.get('agility', 0)),
            'dexterity': int(stats.get('dexterity', 0)),
            'intuition': int(stats.get('intuition', 0)),
            'strength':  int(stats.get('strength', 0)),
        },
        'race_id':             int(getattr(session, 'race_id', 0) or 0),
        'level':               int(getattr(session, 'level', 1) or 1),
        'stance':              getattr(session, 'stance', 'neutral') or 'neutral',
        'profession_name':     getattr(session, 'profession_name', '') or '',
        'stamina':             int(getattr(session, 'stamina', 0) or 0),
        'smr_off_bonus':       int(getattr(session, 'smr_off_bonus', 0) or 0),
        'smr_def_bonus':       int(getattr(session, 'smr_def_bonus', 0) or 0),
        'encumbrance_penalty': int(getattr(session, 'encumbrance_penalty', 0) or 0),
        'armor_action_penalty': int(getattr(session, 'armor_action_penalty', 0) or 0),
        'weapon_techniques':   _get_learned_techniques(session),
        'technique_cooldowns': getattr(session, 'technique_cooldowns', {}) or {},
        'reaction_triggers':   _build_trigger_snapshot(session),
        'gender':              getattr(session, 'gender', 'neutral') or 'neutral',
    }


def _get_learned_techniques(session) -> dict:
    """Return {mnemonic: rank} for all techniques the player has learned."""
    return getattr(session, 'weapon_techniques', {}) or {}


def _creature_to_entity(creature) -> dict:
    """Build entity dict from a creature object."""
    sr = getattr(creature, 'skill_ranks', {}) or {}
    st = getattr(creature, 'stats', {}) or {}
    return {
        'skill_ranks': dict(sr),
        'stats':       dict(st),
        'race_id':     0,
        'level':       int(getattr(creature, 'level', 1) or 1),
        'stance':      getattr(creature, 'stance', 'neutral') or 'neutral',
        'name':        getattr(creature, 'name', 'creature') or 'creature',
        'smr_off_bonus': 0,
        'smr_def_bonus': 0,
        'encumbrance_penalty': 0,
        'armor_action_penalty': 0,
        'gender': getattr(creature, 'gender', 'neutral') or 'neutral',
    }


# ── Room target gathering ─────────────────────────────────────────────────────

def _gather_room_targets(session, server, target_name: str, is_aoe: bool) -> list:
    """
    Return a list of creature objects in the room.
    For AoE: up to MOC-limited count of all hostiles.
    For single: find by name.
    """
    room_id = getattr(session, 'current_room_id', None)
    if not room_id:
        return []

    creatures = []
    if hasattr(server, 'creatures'):
        room_creatures = server.creatures.get_creatures_in_room(room_id) or []
        for c in room_creatures:
            if getattr(c, 'is_alive', True):
                creatures.append(c)

    if is_aoe or target_name == '__room__':
        moc  = _get_moc_ranks(session)
        cap  = moc_hits(moc)
        return creatures[:cap]

    if target_name and target_name != '__direct__':
        name_lower = target_name.lower()
        for c in creatures:
            if name_lower in (getattr(c, 'name', '') or '').lower():
                return [c]

    return []


# ── Effect application ────────────────────────────────────────────────────────

_EFFECT_DISPATCH = {
    'stunned':           lambda e, d, mag: apply_stun(e, d),
    'staggered':         lambda e, d, mag: apply_stagger(e, d),
    'prone':             lambda e, d, mag: apply_prone(e, d),
    'vulnerable':        lambda e, d, mag: apply_vulnerable(e, d),
    'crippled':          lambda e, d, mag: apply_crippled(e, d),
    'slowed':            lambda e, d, mag: apply_slowed(e, d),
    'rooted':            lambda e, d, mag: apply_effect(e, 'rooted', d),
    'dazed':             lambda e, d, mag: apply_effect(e, 'dazed', d),
    'disoriented':       lambda e, d, mag: apply_effect(e, 'disoriented', d),
    'pinned':            lambda e, d, mag: apply_effect(e, 'pinned', d),
    'evasiveness':       lambda e, d, mag: apply_effect(e, 'evasiveness', d),
    'weakened_armament': lambda e, d, mag: apply_effect(e, 'weakened_armament', d),
    'frenzy':            lambda e, d, mag: apply_effect(e, 'frenzy', d),
    'slashing_strikes':  lambda e, d, mag: apply_effect(e, 'slashing_strikes', d),
    'forceful_blows':    lambda e, d, mag: apply_effect(e, 'forceful_blows', d),
    'fortified_stance':  lambda e, d, mag: apply_effect(e, 'fortified_stance', d),
    'parry_bonus':       lambda e, d, mag: apply_effect(e, 'parry_bonus', d, magnitude=mag),
    'evade_bonus':       lambda e, d, mag: apply_effect(e, 'evade_bonus', d, magnitude=mag),
    'ds_bonus':          lambda e, d, mag: apply_effect(e, 'ds_bonus', d, magnitude=mag),
    'avoid_engagement_bonus': lambda e, d, mag: apply_effect(e, 'avoid_engagement_bonus', d),
    'enhance_dexterity': lambda e, d, mag: apply_effect(e, 'enhance_dexterity', d, magnitude=mag),
}


def _apply_effects(result: dict, session, targets: list, server):
    """Apply all effects from a Lua technique result to session and/or targets."""
    effects = result.get('effects_applied') or []
    if not isinstance(effects, list):
        try:
            effects = list(effects)
        except Exception:
            effects = []

    for eff in effects:
        if not isinstance(eff, dict):
            continue
        effect_name = str(eff.get('effect', ''))
        duration    = float(eff.get('duration', 0) or 0)
        magnitude   = float(eff.get('magnitude', 1) or 1)
        tgt_label   = str(eff.get('target', 'defender'))

        if effect_name == 'remove_recent_ebp':
            clear_reaction_trigger(session, 'recent_parry')
            clear_reaction_trigger(session, 'recent_evade')
            clear_reaction_trigger(session, 'recent_block')
            continue

        dispatcher = _EFFECT_DISPATCH.get(effect_name)

        if tgt_label in ('self', 'self_and_party'):
            if dispatcher and duration > 0:
                try:
                    dispatcher(session, duration, magnitude)
                except Exception as e:
                    log.warning("Effect apply error %s on self: %s", effect_name, e)
            if tgt_label == 'self_and_party' and hasattr(server, 'sessions'):
                for s in server.sessions.get_room_sessions(
                    getattr(session, 'current_room_id', None)
                ):
                    if s is not session and dispatcher and duration > 0:
                        try:
                            dispatcher(s, duration, magnitude)
                        except Exception:
                            pass
        else:
            # Apply to each target
            for tgt in targets:
                if dispatcher and duration > 0:
                    try:
                        dispatcher(tgt, duration, magnitude)
                    except Exception as e:
                        log.warning("Effect apply error %s on target: %s", effect_name, e)

    # Per-target effects in AoE results
    for aoe_entry in (result.get('aoe_results') or []):
        if not isinstance(aoe_entry, dict) or not aoe_entry.get('success'):
            continue
        target_name = aoe_entry.get('target', '')
        tgt_obj     = next((t for t in targets
                            if (getattr(t, 'name', '') or '').lower() == target_name.lower()),
                           None)
        if not tgt_obj:
            continue
        for eff in (aoe_entry.get('effects') or []):
            if not isinstance(eff, dict):
                continue
            eff_name = str(eff.get('effect', ''))
            dur      = float(eff.get('duration', 0) or 0)
            mag      = float(eff.get('magnitude', 1) or 1)
            dispatcher = _EFFECT_DISPATCH.get(eff_name)
            if dispatcher and dur > 0:
                try:
                    dispatcher(tgt_obj, dur, mag)
                except Exception as e:
                    log.warning("AoE effect %s error: %s", eff_name, e)


# ── Stamina drain ─────────────────────────────────────────────────────────────

def _drain_stamina(session, amount: int, server):
    if amount <= 0:
        return
    current = int(getattr(session, 'stamina', 0) or 0)
    session.stamina = max(0, current - amount)
    try:
        db = server.db
        db.execute_query(
            "UPDATE characters SET stamina = %s WHERE id = %s",
            (session.stamina, session.character_id)
        )
    except Exception as e:
        log.warning("Stamina drain DB error: %s", e)


# ── Roundtime assignment ──────────────────────────────────────────────────────

def _assign_roundtime(session, result: dict):
    rt = int(result.get('roundtime', 0) or 0)
    if result.get('rt_from_attack'):
        # RT = current attack RT + rt_mod
        current_rt = int(getattr(session, 'base_attack_roundtime', 3) or 3)
        mod        = int(result.get('rt_mod', 0) or 0)
        rt         = max(1, current_rt + mod)
    if rt > 0:
        session.roundtime = rt


# ── Deferred AoE (Volley) ─────────────────────────────────────────────────────

def _schedule_volley(result: dict, session, server):
    """Schedule Volley impact for next round."""
    delay      = int(result.get('deferred_delay', 1)) * 3   # ~3s per round
    num_shots  = int(result.get('num_shots', 1) or 1)
    snapshot   = result.get('attacker_snapshot', {})
    room_id    = getattr(session, 'current_room_id', None)

    async def _impact():
        await asyncio.sleep(delay)
        try:
            targets = _gather_room_targets(session, server, '__room__', is_aoe=True)
            if not targets:
                return
            smr_opts = snapshot.get('smr_opts', {})
            msgs = ["Arrows rain down from above!"]
            for _ in range(num_shots):
                import random as _random
                tgt = _random.choice(targets)
                # Quick attack resolve using smr_engine
                from server.core.engine.combat.combat_engine import resolve_attack_hit
                hit_msg = await resolve_attack_hit(session, tgt, server,
                                                   damage_type='puncture',
                                                   smr_opts=smr_opts)
                if hit_msg:
                    msgs.append(f"An arrow from above strikes {tgt.name}!  {hit_msg}")
            # Broadcast to room
            if hasattr(server, 'sessions'):
                for s in server.sessions.get_room_sessions(room_id) or []:
                    await s.send_line("\n".join(msgs))
        except Exception as e:
            log.error("Volley impact error: %s", e)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_impact())


# ── Main public entry point ───────────────────────────────────────────────────

async def execute_technique(session, mnemonic: str, target_name: str,
                            server, limb: str = '') -> Optional[str]:
    """
    Execute a weapon technique for a player session.
    Returns the message string to send, or None on internal error.

    Called by cmd_weapon() in weapon_techniques.py.
    """
    lua = getattr(server, 'lua', None)
    if not lua or not lua.engine:
        return "Weapon technique system is not available (Lua engine offline)."

    engine = lua.engine

    # Gather targets before calling Lua
    tech_defs = lua.engine.require("weapon_techniques/definitions")
    tech_meta = None
    if tech_defs:
        try:
            tech_meta = lua.engine.lua_to_python(tech_defs[mnemonic])
        except Exception:
            pass

    is_aoe       = tech_meta and tech_meta.get('type') in ('aoe',) if tech_meta else False
    targets      = _gather_room_targets(session, server, target_name, is_aoe)
    target_obj   = targets[0] if targets and not is_aoe else None

    # Build the full player snapshot for Lua
    player_snap  = _session_to_entity(session)
    player_snap['weapon_techniques'] = _get_learned_techniques(session)
    player_snap['technique_cooldowns'] = getattr(session, 'technique_cooldowns', {}) or {}
    player_snap['reaction_triggers']  = _build_trigger_snapshot(session)

    # Build args table for Lua engine
    args = {
        'subcmd':      mnemonic,
        'arg':         '',
        'target':      target_name,
        'limb':        limb,
    }

    # Inject Python-side target objects into player snap (as serialized dicts)
    if is_aoe and targets:
        player_snap['_aoe_targets'] = [_creature_to_entity(t) for t in targets]
    elif target_obj:
        player_snap['_single_target'] = _creature_to_entity(target_obj)

    # Call Lua engine
    try:
        lua_engine   = lua.engine
        engine_table = lua_engine.require("weapon_techniques/engine")

        # Prepare target/targets for Lua
        lua_player = lua_engine.python_to_lua(player_snap)
        lua_args   = lua_engine.python_to_lua(args)

        # Attach targets directly to lua_player for handler access
        if is_aoe and targets:
            lua_targets = lua_engine.python_to_lua(
                [_creature_to_entity(t) for t in targets])
            lua_player['targets'] = lua_targets
        elif target_obj:
            lua_player['target'] = lua_engine.python_to_lua(_creature_to_entity(target_obj))

        raw = lua_engine.call_hook(engine_table, 'onWeaponVerb', lua_player, lua_args)
        if raw is None:
            return "Weapon technique system returned no result."
        result = lua_engine.lua_to_python(raw)
    except Exception as e:
        log.error("execute_technique Lua error [%s]: %s", mnemonic, e, exc_info=True)
        return f"An error occurred executing {mnemonic}."

    if not isinstance(result, dict):
        return "Weapon technique system error: unexpected result format."

    # Non-ok means validation failure (wrong profession, no trigger, etc.)
    if not result.get('ok'):
        return result.get('message', 'Technique failed.')

    # Apply all side effects
    _drain_stamina(session, int(result.get('stamina_spent', 0) or 0), server)
    _assign_roundtime(session, result)
    _apply_effects(result, session, targets, server)

    # Handle deferred AoE (Volley)
    if result.get('is_deferred_aoe'):
        _schedule_volley(result, session, server)

    # Update cooldown back to session (Lua set it on the snapshot)
    new_cds = result.get('technique_cooldowns')
    if new_cds and isinstance(new_cds, dict):
        session.technique_cooldowns = new_cds

    # Sync reaction trigger changes back from Lua snapshot
    new_rt = result.get('reaction_triggers')
    if isinstance(new_rt, dict) and hasattr(session, 'reaction_triggers'):
        # Clear any triggers that Lua consumed (set to false in snapshot)
        for k, v in new_rt.items():
            if not v:
                session.reaction_triggers.pop(k, None)

    return result.get('message', '')


# ── Creature technique execution ──────────────────────────────────────────────

async def creature_use_technique(creature, target_session, mnemonic: str,
                                  creature_rank: int, server) -> Optional[str]:
    """
    Execute a weapon technique for a creature against a player.
    Called by combat_engine during creature combat turns.
    Returns the message string to broadcast to the room, or None on error.
    """
    lua = getattr(server, 'lua', None)
    if not lua or not lua.engine:
        return None

    lua_engine   = lua.engine
    engine_table = lua_engine.require("weapon_techniques/engine")
    if not engine_table:
        return None

    creature_snap = _creature_to_entity(creature)
    target_snap   = _session_to_entity(target_session)

    lua_creature = lua_engine.python_to_lua(creature_snap)
    lua_target   = lua_engine.python_to_lua(target_snap)
    lua_creature['target'] = lua_target

    try:
        raw    = lua_engine.call_hook(engine_table, 'onCreatureTechnique',
                                      lua_creature, lua_target, mnemonic, creature_rank)
        if raw is None:
            return None
        result = lua_engine.lua_to_python(raw)
    except Exception as e:
        log.error("creature_use_technique error [%s]: %s", mnemonic, e)
        return None

    if not isinstance(result, dict) or not result.get('ok'):
        return None

    # Apply effects to the target (player session)
    _apply_effects(result, target_session, [target_session], server)

    return result.get('message', '')


# ── Grant techniques on skill training ───────────────────────────────────────

async def check_and_grant_techniques(session, skill_name: str,
                                      new_ranks: int, server) -> List[str]:
    """
    Called after a player trains weapon skill ranks.
    Returns list of grant messages to send to the player.
    """
    lua = getattr(server, 'lua', None)
    if not lua or not lua.engine:
        return []

    lua_engine   = lua.engine
    engine_table = lua_engine.require("weapon_techniques/engine")
    if not engine_table:
        return []

    player_snap = _session_to_entity(session)
    lua_player  = lua_engine.python_to_lua(player_snap)

    try:
        raw     = lua_engine.call_hook(engine_table, 'onAutoGrant',
                                       lua_player, skill_name, new_ranks)
        if raw is None:
            return []
        granted = lua_engine.lua_to_python(raw)
    except Exception as e:
        log.error("check_and_grant_techniques error: %s", e)
        return []

    if not isinstance(granted, list) or not granted:
        return []

    messages = []
    wt = getattr(session, 'weapon_techniques', {}) or {}

    for entry in granted:
        if not isinstance(entry, dict):
            continue
        mnemonic = str(entry.get('mnemonic', ''))
        name     = str(entry.get('name', mnemonic))
        new_rank = int(entry.get('new_rank', 1))
        is_new   = bool(entry.get('is_new', True))

        # Persist to DB
        try:
            db = server.db
            db.execute_query("""
                INSERT INTO character_weapon_techniques (character_id, technique_id, current_rank)
                SELECT %s, wt.id, %s
                FROM weapon_techniques wt
                WHERE wt.mnemonic = %s
                ON DUPLICATE KEY UPDATE current_rank = VALUES(current_rank)
            """, (session.character_id, new_rank, mnemonic))
        except Exception as e:
            log.error("Grant technique DB error [%s]: %s", mnemonic, e)

        # Update in-memory state
        wt[mnemonic] = new_rank
        session.weapon_techniques = wt

        if is_new:
            messages.append(
                colorize(f"You have learned the {name} weapon technique!", TextPresets.HIGHLIGHT)
            )
        else:
            messages.append(
                colorize(f"Your {name} technique has improved to rank {new_rank}!", TextPresets.HIGHLIGHT)
            )

    return messages


# ── Session loader ────────────────────────────────────────────────────────────

def load_techniques_for_session(session, db):
    """
    Load all learned techniques from DB into session.weapon_techniques dict.
    Call this during session login / character load.
    """
    try:
        rows = db.fetch_all("""
            SELECT wt.mnemonic, cwt.current_rank
            FROM character_weapon_techniques cwt
            JOIN weapon_techniques wt ON wt.id = cwt.technique_id
            WHERE cwt.character_id = %s
        """, (session.character_id,))
        session.weapon_techniques = {row['mnemonic']: row['current_rank'] for row in (rows or [])}
    except Exception as e:
        log.error("load_techniques_for_session error: %s", e)
        session.weapon_techniques = {}


def available_technique_summaries(session, server) -> List[dict]:
    """
    Return technique summaries currently available from the player's training.
    Each row: {name, mnemonic, category, weapon_skill, min_ranks}
    """
    lua = getattr(server, 'lua', None)
    if not lua or not lua.engine:
        return []

    try:
        defs_lua = lua.engine.require("weapon_techniques/definitions")
        defs = lua.engine.lua_to_python(defs_lua) if defs_lua else {}
    except Exception as e:
        log.error("available_technique_summaries Lua error: %s", e)
        return []

    professions = (lua.get_professions() or {}).get("professions", [])
    profession_name = (
        getattr(session, "profession_name", None)
        or getattr(session, "profession", None)
        or next((row.get("name") for row in professions if int(row.get("id", 0) or 0) == int(getattr(session, "profession_id", 0) or 0)), "")
        or ""
    )
    profession_key = str(profession_name).strip().lower()
    if not profession_key:
        return []

    category_labels = {
        "brawling": "Brawling",
        "blunt": "Blunt Weapons",
        "edged": "Edged Weapons",
        "polearm": "Polearm Weapons",
        "ranged": "Ranged Weapons",
        "twohanded": "Two-Handed Weapons",
    }

    summaries = []
    for mnemonic, tech in (defs or {}).items():
        if not isinstance(tech, dict):
            continue
        if str(tech.get("mnemonic") or "").strip().lower() != str(mnemonic).strip().lower():
            continue

        available_to = [str(v).strip().lower() for v in (tech.get("available_to") or [])]
        if profession_key not in available_to:
            continue

        skill_key = str(tech.get("weapon_skill") or "").strip().lower()
        if not skill_key:
            continue
        current_ranks = _get_skill_ranks(session, skill_key)
        thresholds = tech.get("rank_thresholds") or []
        min_ranks = int((thresholds[0] if thresholds else tech.get("min_ranks", 0)) or 0)
        if current_ranks < min_ranks:
            continue

        category_key = str(tech.get("category") or "").strip().lower()
        summaries.append({
            "name": str(tech.get("name") or mnemonic).strip(),
            "mnemonic": str(tech.get("mnemonic") or mnemonic).strip(),
            "category": category_labels.get(category_key, category_key.title()),
            "weapon_skill": skill_key.replace("_", " ").title(),
            "min_ranks": min_ranks,
        })

    summaries.sort(key=lambda row: (int(row["min_ranks"]), row["category"], row["name"]))
    return summaries
