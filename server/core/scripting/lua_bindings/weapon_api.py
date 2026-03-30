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
from typing import Optional, List, Dict, Any

from server.core.engine.action_feedback import summarize_applied_effects
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

_SKILL_KEY_TO_ID = {
    "edged_weapons": 5,
    "blunt_weapons": 6,
    "two_handed_weapons": 7,
    "ranged_weapons": 8,
    "polearm_weapons": 10,
    "brawling": 11,
    "multi_opponent_combat": 12,
    "combat_maneuvers": 4,
    "dodging": 14,
}


def _get_skill_ranks(session, skill_key: str) -> int:
    skills = getattr(session, 'skills', {}) or {}
    normalized = str(skill_key or '').strip().lower()
    skill_id = _SKILL_KEY_TO_ID.get(normalized)
    d = (
        skills.get(normalized)
        or skills.get(normalized.replace('_', ' '))
        or (skills.get(skill_id) if skill_id is not None else None)
        or (skills.get(str(skill_id)) if skill_id is not None else None)
    )
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
        normalized = str(key or '').strip().lower()
        skill_id = _SKILL_KEY_TO_ID.get(normalized)
        d = (
            skills.get(normalized)
            or skills.get(normalized.replace('_', ' '))
            or (skills.get(skill_id) if skill_id is not None else None)
            or (skills.get(str(skill_id)) if skill_id is not None else None)
            or {}
        )
        return int(d.get('ranks', 0)) if isinstance(d, dict) else int(d or 0)

    stats = getattr(session, 'stats', {}) or {}
    profession_name = _resolve_profession_name(session, getattr(session, "server", None))

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
        'profession_name':     profession_name,
        'stamina':             int(getattr(session, 'stamina_current', 0) or 0),
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
    room_id = _session_room_id(session)
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

    applied_rows = []

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
                    applied_rows.append({
                        "effect": effect_name,
                        "entity": session,
                        "target_label": "self",
                    })
                except Exception as e:
                    log.warning("Effect apply error %s on self: %s", effect_name, e)
            if tgt_label == 'self_and_party' and hasattr(server, 'sessions'):
                for s in server.sessions.get_room_sessions(
                    _session_room_id(session)
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
                        applied_rows.append({
                            "effect": effect_name,
                            "entity": tgt,
                            "target_label": "defender",
                        })
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
                    applied_rows.append({
                        "effect": eff_name,
                        "entity": tgt_obj,
                        "target_label": "defender",
                    })
                except Exception as e:
                    log.warning("AoE effect %s error: %s", eff_name, e)
    return applied_rows


# ── Stamina drain ─────────────────────────────────────────────────────────────

def _resolve_profession_name(session, server=None) -> str:
    explicit = getattr(session, "profession_name", None) or getattr(session, "profession", None)
    if explicit:
        return str(explicit).strip().lower()

    lua = getattr(server, "lua", None) if server else None
    if lua:
        try:
            professions = (lua.get_professions() or {}).get("professions", [])
            prof_id = int(getattr(session, "profession_id", 0) or 0)
            for row in professions:
                if int(row.get("id", 0) or 0) == prof_id:
                    name = str(row.get("name") or "").strip().lower()
                    if name:
                        return name
        except Exception:
            pass
    return ""


def _normalize_weapon_skill_key(raw_skill: str) -> str:
    raw = str(raw_skill or "").strip().lower()
    return _CAT_TO_SKILL_KEY.get(raw, raw)


def _weapon_matches_category(item: Optional[dict], category: str) -> bool:
    if not item or item.get("item_type") != "weapon":
        return False
    return str(item.get("weapon_category") or item.get("weapon_type") or "").strip().lower() == str(category or "").strip().lower()


def _active_hand_items(session) -> list[tuple[str, Optional[dict]]]:
    return [
        ("right_hand", getattr(session, "right_hand", None)),
        ("left_hand", getattr(session, "left_hand", None)),
    ]


def _session_room_id(session) -> Optional[int]:
    room = getattr(session, "current_room", None)
    if room is not None and getattr(room, "id", None) is not None:
        return int(room.id)
    room_id = getattr(session, "current_room_id", None)
    return int(room_id) if room_id is not None else None


def _split_assault_messages(message: str, round_count: int) -> tuple[str, list[str], str]:
    lines = [line for line in str(message or "").splitlines() if line.strip()]
    if not lines:
        return "", [], ""
    if round_count <= 0:
        return "\n".join(lines), [], ""

    start_message = lines[0]
    round_messages = lines[1:1 + round_count]
    final_message = "\n".join(lines[1 + round_count:]).strip()
    return start_message, round_messages, final_message


def _technique_damage_scale(attack_spec: dict) -> float:
    if attack_spec.get("minor"):
        return 0.65
    if attack_spec.get("moderate"):
        return 0.85
    return 1.0


def _technique_weapon_hand(session, weapon: Optional[dict]) -> str:
    if weapon and getattr(session, "right_hand", None) is weapon:
        return "right"
    if weapon and getattr(session, "left_hand", None) is weapon:
        return "left"
    return "right"


def _stance_order() -> list[str]:
    return ["offensive", "advance", "forward", "neutral", "guarded", "defensive"]


def _shift_creature_stance_more_offensive(creature):
    current = (getattr(creature, "stance", "neutral") or "neutral").lower()
    order = _stance_order()
    if current not in order:
        current = "neutral"
    idx = order.index(current)
    if idx > 0:
        creature.stance = order[idx - 1]


def _validate_technique_loadout(session, tech_meta: dict) -> tuple[bool, str]:
    category = str(tech_meta.get("category") or "").strip().lower()
    gear = str(tech_meta.get("offensive_gear") or "").strip().lower()
    right = getattr(session, "right_hand", None)
    left = getattr(session, "left_hand", None)

    if category == "brawling":
        for _hand, item in _active_hand_items(session):
            if not item:
                continue
            if item.get("item_type") == "shield":
                return False, "You need both hands free of shields to use that brawling technique."
            if item.get("item_type") == "weapon" and not _weapon_matches_category(item, "brawling"):
                return False, "You need your hands free of weapons to use that brawling technique."
        return True, ""

    expected_category = category
    if gear == "right_hand":
        if not _weapon_matches_category(right, expected_category):
            return False, f"You need a {expected_category.replace('twohanded', 'two-handed')} weapon readied in your right hand."
        if left and left.get("item_type") == "shield" and expected_category in ("twohanded", "polearm", "ranged"):
            return False, "That technique requires your off-hand free."
        return True, ""

    matching_hands = [hand for hand, item in _active_hand_items(session) if _weapon_matches_category(item, expected_category)]
    if not matching_hands:
        label = expected_category.replace("twohanded", "two-handed")
        return False, f"You need an appropriate {label} weapon readied to use that technique."

    if gear == "both_hands":
        for _hand, item in _active_hand_items(session):
            if item and item.get("item_type") == "shield":
                return False, "You need both hands free of shields to use that technique."
        if expected_category in ("twohanded", "polearm", "ranged") and right and left and right is not left:
            return False, "That technique requires both hands committed to the proper weapon."

    if expected_category == "ranged":
        from server.core.commands.player.combat import _find_ready_ammo
        ready_ammo = (
            _find_ready_ammo(session, "arrow")
            or _find_ready_ammo(session, "bolt")
            or _find_ready_ammo(session, "pellet")
            or _find_ready_ammo(session, "stone")
        )
        if not ready_ammo:
            return False, "You need appropriate ammunition readied before using that ranged technique."

    return True, ""


def _clear_weapon_assault_state(session):
    state = getattr(session, "weapon_assault_state", None) or {}
    task = state.get("task")
    current_task = None
    try:
        current_task = asyncio.current_task()
    except RuntimeError:
        current_task = None
    if task and not task.done() and task is not current_task:
        task.cancel()
    session.weapon_assault_state = None


def stop_active_weapon_assault(session) -> tuple[bool, str]:
    state = getattr(session, "weapon_assault_state", None) or {}
    if not state:
        return False, "You are not committed to an assault right now."
    task = state.get("task")
    if task and not task.done():
        task.cancel()
    session.weapon_assault_state = None
    if hasattr(session, "set_roundtime"):
        session.set_roundtime(0)
    return True, "You break off your assault."


async def _apply_technique_hit(session, creature, server, roll: dict, attack_spec: dict,
                               technique_name: str = "", aimed_location: str = "") -> dict:
    from server.core.engine.combat.combat_engine import (
        CRIT_DIVISORS, CRIT_MESSAGES, LETHAL_THRESHOLDS,
        LOCATION_DAMAGE_MULT, LOCATION_CRIT_DIV_MULT, SEVERABLE_LOCATIONS,
        _enter_combat, _exit_combat, _refresh_combat, _resolve_damage_profile,
        _get_player_weapon,
    )
    from server.core.engine.combat.material_combat import resolve_flare, get_crit_phantom
    from server.core.protocol.colors import combat_damage, combat_crit, combat_death
    from server.core.scripting.loaders.body_types_loader import resolve_aim, random_location

    if not creature or getattr(creature, "is_dead", False):
        return {"killed": True, "damage": 0, "location": ""}

    weapon, weapon_hand = _get_player_weapon(session)
    weapon_hand = _technique_weapon_hand(session, weapon) if weapon else weapon_hand

    raw_damage_type = str(attack_spec.get("damage_type") or "").strip().lower()
    if not raw_damage_type or raw_damage_type == "weapon":
        raw_damage_type = (weapon.get("damage_type", "crush") if weapon else "crush")
    elif raw_damage_type == "unbalance":
        raw_damage_type = "crush"

    base_df = None
    if weapon:
        base_df = weapon.get("damage_factor", 0) or None
    profile = _resolve_damage_profile(
        raw_damage_type,
        getattr(creature, "armor_asg", 5),
        base_df,
    )
    damage_type = profile["damage_type"]
    weapon_df = float(profile["df"] or 0.25) * _technique_damage_scale(attack_spec)

    requested_location = str(attack_spec.get("limb") or aimed_location or "").strip().lower()
    body_type = getattr(creature, "body_type", "biped") or "biped"
    location = resolve_aim(body_type, requested_location) if requested_location else None
    if not location:
        location = random_location(body_type)

    total = int((roll or {}).get("total", 100) or 100)
    if total <= 100:
        return {"killed": False, "damage": 0, "location": location}

    loc_df_mult = LOCATION_DAMAGE_MULT.get(location, 1.0)
    raw_damage = max(1, int((total - 100) * weapon_df * loc_df_mult))

    crit_phantom = int(attack_spec.get("cer_bonus", 0) or 0)
    if weapon and bool(attack_spec.get("flares_enabled", True)):
        crit_phantom += get_crit_phantom(weapon, getattr(server, "lua", None))
    adj_raw = raw_damage + crit_phantom
    crit_divisor = max(1, int(CRIT_DIVISORS.get(getattr(creature, "armor_asg", 5), 5) * LOCATION_CRIT_DIV_MULT.get(location, 1.0)))
    crit_rank_max = min(9, adj_raw // crit_divisor)
    if crit_rank_max > 0:
        import random as _random
        crit_rank_min = max(1, (crit_rank_max + 1) // 2)
        crit_rank = _random.randint(crit_rank_min, crit_rank_max)
    else:
        crit_rank = 0

    hp_damage = max(1, int((total - 100) * (0.42 + (weapon_df * 0.25)) * loc_df_mult) + crit_rank * 3)
    actual_damage = creature.take_damage(hp_damage)

    flare_result = None
    if weapon and bool(attack_spec.get("flares_enabled", True)):
        flare_result = await resolve_flare(session, creature, weapon, weapon_hand)
        if flare_result and int(flare_result.get("damage", 0) or 0) > 0:
            creature.take_damage(int(flare_result["damage"]))

    await session.send_line(combat_damage(actual_damage, location))
    if crit_rank > 0:
        crit_msgs = CRIT_MESSAGES.get(damage_type, CRIT_MESSAGES["slash"])
        crit_msg = crit_msgs.get(crit_rank, "Critical hit!")
        await session.send_line(combat_crit(crit_rank, crit_msg))

    if flare_result:
        await session.send_line(colorize(f"  {flare_result.get('attacker_msg', '')}", TextPresets.COMBAT_HIT))
        if int(flare_result.get("damage", 0) or 0) > 0:
            await session.send_line(colorize(
                f"  The flare deals {int(flare_result['damage'])} additional points of damage!",
                TextPresets.COMBAT_HIT,
            ))
        room_msg = flare_result.get("room_msg", "")
        if room_msg:
            await server.world.broadcast_to_room(
                session.current_room.id,
                colorize(f"  {room_msg}", TextPresets.COMBAT_HIT),
                exclude=[session],
            )

    if attack_spec.get("force_target_stance"):
        _shift_creature_stance_more_offensive(creature)

    if crit_rank >= 1:
        old_sev = creature.wounds.get(location, 0)
        new_sev = creature.apply_wound(location, crit_rank)
        if new_sev > old_sev:
            await session.send_line(colorize(
                f"  {getattr(creature, 'full_name', creature.name).capitalize()} suffers a wound to its {location}!",
                TextPresets.COMBAT_HIT,
            ))
            impairment = creature.evaluate_combat_impairment(location, old_sev, new_sev)
            if impairment.get("dropped_weapon"):
                await session.send_line(colorize(
                    f"  {getattr(creature, 'full_name', creature.name).capitalize()} drops its weapon as the limb goes slack!",
                    TextPresets.COMBAT_HIT,
                ))
            if impairment.get("severed") and location in SEVERABLE_LOCATIONS:
                await session.send_line(colorize(
                    f"  The strike severs {getattr(creature, 'full_name', creature.name)}'s {location}!",
                    TextPresets.COMBAT_HIT,
                ))
            if impairment.get("stance_shift"):
                creature.stance = impairment["stance_shift"]

    if crit_rank >= 3:
        stun_dur = crit_rank * 2
        creature.stun(stun_dur)
        await session.send_line(colorize(f"  The {creature.name} is stunned!", TextPresets.COMBAT_HIT))
        try:
            from server.core.engine.combat.status_effects import apply_bleed, apply_fear
            apply_bleed(creature, crit_rank, attacker=session)
            await session.send_line(colorize(
                f"  {getattr(creature, 'full_name', creature.name).capitalize()} is bleeding!",
                TextPresets.COMBAT_HIT,
            ))
            if crit_rank >= 6:
                apply_fear(creature, duration=30)
                await session.send_line(colorize(
                    f"  {getattr(creature, 'full_name', creature.name).capitalize()} looks terrified!",
                    TextPresets.COMBAT_HIT,
                ))
        except ImportError:
            pass

    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name}'s {technique_name or 'technique'} strikes {getattr(creature, 'full_name', creature.name)} for {actual_damage} points of damage to the {location}.",
        exclude=session,
    )

    killed = False
    if getattr(creature, "is_dead", False) or crit_rank >= LETHAL_THRESHOLDS.get(location, 99):
        if not getattr(creature, "is_dead", False):
            creature.take_damage(getattr(creature, "health_current", 0))
        killed = True
        await session.send_line(combat_death(getattr(creature, "full_name", creature.name).capitalize()))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"  {getattr(creature, 'full_name', creature.name).capitalize()} falls to the ground dead!",
            exclude=session,
        )
        server.creatures.mark_dead(creature)
        session.target = None
        remaining = [
            c for c in server.creatures.get_creatures_in_room(session.current_room.id)
            if getattr(c, "alive", True) and getattr(c, "aggressive", False) and c is not creature
        ]
        if not remaining:
            _exit_combat(server, session)
        if hasattr(server, "experience"):
            from server.core.commands.player.party import award_party_kill_xp
            await award_party_kill_xp(session, creature, server)
    else:
        _enter_combat(server, session, creature)
        _refresh_combat(server, session, creature)

    return {"killed": killed, "damage": actual_damage, "location": location}


async def _apply_attack_specs(session, target_obj, server, roll: dict, attack_specs: list[dict],
                              technique_name: str = "", aimed_location: str = "", shared_flags: Optional[dict] = None) -> bool:
    killed = False
    shared_flags = shared_flags or {}
    for attack_spec in attack_specs or []:
        if not isinstance(attack_spec, dict):
            continue
        spec = dict(attack_spec)
        for key, value in shared_flags.items():
            spec.setdefault(key, value)
        outcome = await _apply_technique_hit(
            session, target_obj, server, roll, spec,
            technique_name=technique_name, aimed_location=aimed_location,
        )
        killed = killed or bool(outcome.get("killed"))
        if killed:
            break
    return killed


async def _apply_completion_effects(session, server, targets: list, effects: list[dict]):
    if effects:
        _apply_effects({"effects_applied": effects}, session, targets, server)


def _assault_effects_for_partial_execution(mnemonic: str, tech: dict, executed_rounds: list[dict], completed_full: bool) -> list[dict]:
    effects: list[dict] = []
    successes = [entry for entry in executed_rounds if entry.get("success")]
    rank = int((tech or {}).get("_player_rank", 0) or 0)

    if mnemonic in {"fury", "pummel", "flurry", "thrash", "barrage"} and successes:
        if mnemonic == "fury":
            effects.append({"effect": "frenzy", "duration": 120, "target": "self"})
        elif mnemonic == "pummel":
            effects.append({"effect": "forceful_blows", "duration": 120, "target": "self"})
        elif mnemonic == "flurry":
            effects.append({"effect": "slashing_strikes", "duration": 120, "target": "self"})
        elif mnemonic == "thrash":
            effects.append({"effect": "forceful_blows", "duration": 120, "target": "self"})
        elif mnemonic == "barrage":
            effects.append({"effect": "enhance_dexterity", "duration": 120, "magnitude": 10, "target": "self_and_party"})

    if mnemonic in {"fury", "pummel", "flurry", "thrash"}:
        divisor = 10 if mnemonic == "thrash" else 5
        total = 0
        for entry in successes:
            roll = entry.get("roll") or {}
            total += min(10, max(0, int((roll.get("margin", 0) or 0) // divisor)))
        if total > 0:
            effects.append({"effect": "parry_bonus", "duration": 30, "magnitude": total, "target": "self"})

    if mnemonic == "barrage":
        total = 0
        for entry in successes:
            roll = entry.get("roll") or {}
            total += min(10, max(0, int((roll.get("margin", 0) or 0) // 10)))
        if total > 0:
            effects.append({"effect": "evade_bonus", "duration": 30, "magnitude": total, "target": "self"})

    if mnemonic == "gthrusts":
        per_round = int((tech or {}).get("ds_bonus_per_round", 5) or 5)
        ds_total = min(rank * per_round if rank > 0 else len(executed_rounds) * per_round, len(executed_rounds) * per_round)
        if ds_total > 0:
            effects.append({"effect": "ds_bonus", "duration": 15, "magnitude": ds_total, "target": "self"})
        if completed_full:
            effects.append({"effect": "fortified_stance", "duration": int((tech or {}).get("completion_buff_duration", 30) or 30), "target": "self"})

    return effects


async def _start_weapon_assault(session, mnemonic: str, tech_meta: dict, target_obj, result: dict, server) -> str:
    round_results = list(result.get("round_results") or [])
    if not round_results:
        return result.get("message", "")

    start_message, round_messages, final_message = _split_assault_messages(result.get("message", ""), len(round_results))
    targets = [target_obj] if target_obj else []
    strike_delay = max(2, int(result.get("roundtime", tech_meta.get("base_rt", 2)) or 2))

    state: Dict[str, Any] = {
        "mnemonic": mnemonic,
        "target_id": getattr(target_obj, "id", None),
        "target_name": getattr(target_obj, "name", result.get("target") or ""),
        "round_results": round_results,
        "round_messages": round_messages,
        "final_message": final_message,
        "tech_meta": dict(tech_meta or {}),
        "stop_requested": False,
        "task": None,
    }
    state["tech_meta"]["_player_rank"] = int(result.get("rank") or tech_meta.get("_player_rank", 0) or 0)
    session.weapon_assault_state = state
    if hasattr(session, "set_roundtime"):
        session.set_roundtime(strike_delay * len(round_results))

    executed_rounds: list[dict] = []

    async def _resolve_round(index: int) -> bool:
        if not session.connected or getattr(session, "is_dead", False):
            return True
        if state.get("stop_requested"):
            await session.send_line("You break off your assault.")
            return True
        if not target_obj or getattr(target_obj, "is_dead", False):
            await session.send_line("Your assault falters as your target is no longer standing.")
            return True
        if getattr(target_obj, "current_room_id", None) != _session_room_id(session):
            await session.send_line("Your assault ends as your target slips out of reach.")
            return True

        round_result = round_results[index]
        if index < len(round_messages) and round_messages[index]:
            await session.send_line(round_messages[index])
        executed_rounds.append(round_result)
        if round_result.get("success") and round_result.get("damage"):
            killed = await _apply_attack_specs(
                session,
                target_obj,
                server,
                round_result.get("roll") or {},
                [round_result.get("damage")],
                technique_name=str(tech_meta.get("name") or mnemonic),
            )
            if killed:
                return True
        return False

    if start_message:
        await session.send_line(start_message)
    stopped_now = await _resolve_round(0)
    if stopped_now:
        effects = _assault_effects_for_partial_execution(mnemonic, state["tech_meta"], executed_rounds, completed_full=False)
        await _apply_completion_effects(session, server, targets, effects)
        _clear_weapon_assault_state(session)
        if hasattr(session, "set_roundtime"):
            session.set_roundtime(0)
        return ""

    async def _runner():
        completed_full = True
        try:
            for idx in range(1, len(round_results)):
                await asyncio.sleep(strike_delay)
                if await _resolve_round(idx):
                    completed_full = False
                    break
            if completed_full and final_message:
                await session.send_line(final_message)

            effects = _assault_effects_for_partial_execution(
                mnemonic,
                state["tech_meta"],
                executed_rounds,
                completed_full=completed_full and len(executed_rounds) == len(round_results),
            )
            await _apply_completion_effects(session, server, targets, effects)
        except asyncio.CancelledError:
            completed_full = False
        finally:
            _clear_weapon_assault_state(session)
            if hasattr(session, "set_roundtime"):
                session.set_roundtime(0)
            if session.connected:
                await session.send_prompt()

    task = asyncio.create_task(_runner())
    state["task"] = task
    session.weapon_assault_state = state
    return ""


def _drain_stamina(session, amount: int, server):
    if amount <= 0:
        return
    current = int(getattr(session, 'stamina_current', 0) or 0)
    session.stamina_current = max(0, current - amount)
    try:
        db = server.db
        db.execute_query(
            "UPDATE characters SET stamina_current = %s WHERE id = %s",
            (session.stamina_current, session.character_id)
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
        if hasattr(session, "set_roundtime"):
            session.set_roundtime(rt)
        else:
            session.roundtime = rt


# ── Deferred AoE (Volley) ─────────────────────────────────────────────────────

def _schedule_volley(result: dict, session, server):
    """Schedule Volley impact for next round."""
    from types import SimpleNamespace

    delay      = int(result.get('deferred_delay', 1)) * 3   # ~3s per round
    num_shots  = int(result.get('num_shots', 1) or 1)
    snapshot   = result.get('attacker_snapshot', {})
    room_id    = _session_room_id(session)

    async def _impact():
        await asyncio.sleep(delay)
        try:
            targets = _gather_room_targets(session, server, '__room__', is_aoe=True)
            if not targets:
                return
            smr_opts = snapshot.get('smr_opts', {})
            attacker = SimpleNamespace(
                skill_ranks=snapshot.get("skill_ranks", {}) or {},
                stats=snapshot.get("stats", {}) or {},
                race_id=int(snapshot.get("race_id", 0) or 0),
                level=int(snapshot.get("level", 1) or 1),
                stance=snapshot.get("stance", "neutral") or "neutral",
                smr_off_bonus=0,
                smr_def_bonus=0,
                encumbrance_penalty=0,
                armor_action_penalty=0,
            )
            if hasattr(server, 'sessions'):
                for s in server.sessions.get_room_sessions(room_id) or []:
                    await s.send_line("Arrows rain down from above!")
            for _ in range(num_shots):
                import random as _random
                tgt = _random.choice(targets)
                defender = SimpleNamespace(**_creature_to_entity(tgt))
                roll = smr_roll(attacker, defender, smr_opts)
                if not roll.get("success"):
                    await server.world.broadcast_to_room(
                        room_id,
                        f"An arrow from above whistles past {tgt.name} harmlessly.",
                    )
                    continue
                if session.connected and _session_room_id(session) == room_id:
                    await session.send_line(f"An arrow from above strikes {tgt.name}!")
                await _apply_attack_specs(
                    session,
                    tgt,
                    server,
                    roll,
                    [{"damage_type": "puncture", "flares_enabled": False}],
                    technique_name="Volley",
                )
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

    if getattr(session, "weapon_assault_state", None):
        return "You are already committed to an assault.  STOP first if you want to break it off."

    # Gather targets before calling Lua
    tech_defs = lua.engine.require("weapon_techniques/definitions")
    tech_meta = None
    if tech_defs:
        try:
            tech_meta = lua.engine.lua_to_python(tech_defs[mnemonic])
        except Exception:
            pass
    if not tech_meta:
        return "That weapon technique is unavailable right now."

    loadout_ok, loadout_msg = _validate_technique_loadout(session, tech_meta)
    if not loadout_ok:
        return loadout_msg

    is_aoe       = tech_meta and tech_meta.get('type') in ('aoe',) if tech_meta else False
    targets      = _gather_room_targets(session, server, target_name, is_aoe)
    target_obj   = targets[0] if targets and not is_aoe else None
    if not is_aoe and target_name and not target_obj:
        return f"You don't see any '{target_name}' here."

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
    result["rank"] = int(player_snap.get("weapon_techniques", {}).get(mnemonic, 0) or 0)

    if result.get("is_assault") or result.get("round_results"):
        return await _start_weapon_assault(session, mnemonic, tech_meta, target_obj, result, server)

    if result.get("message"):
        await session.send_line(result["message"])

    _assign_roundtime(session, result)

    shared_flags = {
        "force_target_stance": bool(result.get("force_target_stance")),
        "flares_enabled": bool(tech_meta.get("flares_enabled", False)),
    }

    if target_obj and result.get("attack_results") and result.get("smr_result"):
        await _apply_attack_specs(
            session,
            target_obj,
            server,
            result.get("smr_result") or {},
            list(result.get("attack_results") or []),
            technique_name=str(tech_meta.get("name") or mnemonic),
            aimed_location=limb,
            shared_flags=shared_flags,
        )

    for aoe_entry in (result.get("aoe_results") or []):
        if not isinstance(aoe_entry, dict) or not aoe_entry.get("success") or not aoe_entry.get("damage"):
            continue
        target_name_l = str(aoe_entry.get("target") or "").strip().lower()
        target = next(
            (t for t in targets if str(getattr(t, "name", "") or "").strip().lower() == target_name_l),
            None,
        )
        if not target:
            continue
        await _apply_attack_specs(
            session,
            target,
            server,
            aoe_entry.get("roll") or {},
            [aoe_entry.get("damage")],
            technique_name=str(tech_meta.get("name") or mnemonic),
            shared_flags={
                "force_target_stance": bool(aoe_entry.get("force_target_stance")),
                "flares_enabled": bool(tech_meta.get("flares_enabled", False)),
            },
        )

    applied_rows = _apply_effects(result, session, targets, server)
    for line in summarize_applied_effects(server, applied_rows):
        await session.send_line(line)

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

    return ""


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

    try:
        defs_lua = lua_engine.require("weapon_techniques/definitions")
        defs = lua_engine.lua_to_python(defs_lua) if defs_lua else {}
    except Exception:
        defs = {}
    profession_key = _resolve_profession_name(session, server)

    messages = []
    wt = getattr(session, 'weapon_techniques', {}) or {}

    for entry in granted:
        if not isinstance(entry, dict):
            continue
        mnemonic = str(entry.get('mnemonic', ''))
        name     = str(entry.get('name', mnemonic))
        new_rank = int(entry.get('new_rank', 1))
        is_new   = bool(entry.get('is_new', True))

        tech_meta = defs.get(mnemonic) if isinstance(defs, dict) else None
        available_to = [str(v).strip().lower() for v in ((tech_meta or {}).get("available_to") or [])]
        if available_to and profession_key not in available_to:
            continue

        # Persist to DB
        try:
            db = server.db
            db.execute_update("""
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
                colorize(f"You have learned the {name} weapon technique!", TextPresets.LEVEL_UP)
            )
        else:
            messages.append(
                colorize(f"Your {name} technique has improved to rank {new_rank}!", TextPresets.LEVEL_UP)
            )

    return messages


async def reconcile_techniques_for_session(session, server, notify: bool = False) -> List[str]:
    """
    Backfill weapon techniques from the character's current trained weapon skills.
    This is used on session load so previously qualified techniques are not missed
    just because the auto-grant path was broken when the ranks were trained.
    """
    skill_names = (
        "edged_weapons",
        "blunt_weapons",
        "two_handed_weapons",
        "ranged_weapons",
        "polearm_weapons",
        "brawling",
    )
    all_messages: List[str] = []
    for skill_name in skill_names:
        ranks = _get_skill_ranks(session, skill_name)
        if ranks <= 0:
            continue
        messages = await check_and_grant_techniques(session, skill_name, ranks, server)
        if notify and messages:
            all_messages.extend(messages)
    return all_messages


# ── Session loader ────────────────────────────────────────────────────────────

def load_techniques_for_session(session, db):
    """
    Load all learned techniques from DB into session.weapon_techniques dict.
    Call this during session login / character load.
    """
    try:
        conn = db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT wt.mnemonic, cwt.current_rank
                FROM character_weapon_techniques cwt
                JOIN weapon_techniques wt ON wt.id = cwt.technique_id
                WHERE cwt.character_id = %s
            """, (session.character_id,))
            rows = cur.fetchall()
        finally:
            conn.close()
        session.weapon_techniques = {
            str(row.get('mnemonic') or ''): int(row.get('current_rank') or 0)
            for row in (rows or [])
            if row.get('mnemonic')
        }
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

        skill_key = _normalize_weapon_skill_key(str(tech.get("weapon_skill") or "").strip().lower())
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
