"""
combat_maneuver_api.py
----------------------
Lua/SQL runtime bridge for Combat Maneuvers.

This module owns:
  - loading learned maneuver ranks and settings from SQL
  - resolving maneuver metadata from Lua
  - passive and temporary combat modifiers
  - CMAN command parsing / execution dispatch
"""

from __future__ import annotations

import ast
import json
import logging
import math
import operator
import random
import re
import time
from types import SimpleNamespace

from server.core.character_unlocks import has_unlock
from server.core.engine.action_feedback import summarize_applied_effects
from server.core.engine.action_ready import evaluate_ready_rule
from server.core.engine.combat.smr_engine import smr_roll
from server.core.protocol.colors import TextPresets, colorize, roundtime_msg
from server.core.scripting.lua_bindings.weapon_api import (
    _get_skill_ranks,
    _resolve_profession_name,
    clear_reaction_trigger,
    has_reaction_trigger,
    set_reaction_trigger,
)

log = logging.getLogger(__name__)

SKILL_COMBAT_MANEUVERS = 4

_ACTIVATABLE_TYPES = {"attack", "setup", "buff", "aoe", "concentration", "martial_stance"}

_SPECIAL_ALIASES = {
    "coup": "coupdegrace",
    "cdg": "coupdegrace",
    "mightyblow": "mblow",
    "spinattack": "sattack",
    "staggeringblow": "sblow",
    "shieldbash": "sbash",
    "suckerpunch": "spunch",
    "weaponspecialization": "wspec",
    "stanceperfection": "stance",
    "combatmovement": "cmovement",
    "combatmobility": "mobility",
    "combattoughness": "toughness",
    "burstofswiftness": "burst",
    "surgeofstrength": "surge",
    "dustshroud": "shroud",
    "internalpower": "ipower",
    "cunningdefense": "cdefense",
    "combatfocus": "focus",
    "acrobatsleap": "acrobatsleap",
}

_GUILD_SKILL_NAME_BY_MNEMONIC = {
    "berserk": "Berserk",
    "cheapshots": "Cheapshots",
    "disarm": "Disarm Weapon",
    "divert": "Rogue Gambits",
    "feint": "Feint",
    "rgambit": "Rogue Gambits",
    "sattack": "Spin Attack",
    "stance": "Stance Perfection",
    "stunman": "Stun Maneuvers",
    "subdue": "Subdue",
    "sweep": "Sweep",
    "tackle": "Tackle",
}

_GUILD_INTRO_UNLOCKS = {
    "Cheapshots": "rogue_skill_cheapshots_intro",
    "Rogue Gambits": "rogue_skill_rgambit_intro",
    "Stun Maneuvers": "rogue_skill_stunman_intro",
    "Subdue": "rogue_skill_subdue_intro",
    "Sweep": "rogue_skill_sweep_intro",
}

_PASSIVE_PRESETS = {
    "cmovement": {"ds_bonus_per_rank": 2},
    "wspec": {"as_bonus_per_rank": 2},
    "blockspec": {"block_pct_per_rank": 5},
    "evadespec": {"evade_pct_per_rank": 5},
    "parryspec": {"parry_pct_per_rank": 5},
    "cdefense": {"smr_def_bonus_by_rank": [0, 2, 6, 12, 20, 30]},
    "mobility": {"auto_stand": True},
    "toughness": {"hp_bonus_base": 5, "hp_bonus_per_rank": 10},
    "focus": {"td_bonus_per_rank": 2},
}

_STATUS_NAME_MAP = {
    "blind": "blinded",
    "blinded": "blinded",
    "confused": "confused",
    "crippled": "crippled",
    "dazed": "dazed",
    "demoralized": "demoralized",
    "disengaged": "disengaged",
    "disoriented": "disoriented",
    "prone": "prone",
    "shrouded": "shrouded",
    "silenced": "silenced",
    "slowed": "slowed",
    "staggered": "staggered",
    "stunned": "stunned",
    "terrified": "terrified",
    "vulnerable": "vulnerable",
    "weakened_armament": "weakened_armament",
}

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_SAFE_FUNCS = {"abs": abs, "ceil": math.ceil, "floor": math.floor, "max": max, "min": min, "round": round}

_BUFF_PRESETS = {
    "surge": {"duration": 90, "strength_bonus": "12 + (4 * rank)", "label": "Surge of Strength"},
    "burst": {
        "duration": 90,
        "agility_bonus": "12 + (4 * rank)",
        "dexterity_bonus": "6 + (2 * rank)",
        "label": "Burst of Swiftness",
    },
    "ipower": {"heal": "15 + (5 * rank)", "label": "Internal Power"},
    "retreat": {"status": "disengaged", "duration": "5 + (2 * rank)", "label": "Retreat"},
    "shroud": {"status": "shrouded", "duration": "rank + 5", "magnitude": "rank * 15", "hide": True, "label": "Dust Shroud"},
    "kifocus": {"duration": 20, "as_bonus": "8 + (4 * rank)", "consume_on_attack": True, "label": "Ki Focus"},
    "berserk": {"duration": "15 + (5 * rank)", "as_bonus": "rank * 5", "label": "Berserk"},
}

_STANCE_PRESETS = {
    "duckandweave": {"duration": 120, "evade_pct_bonus": 10, "label": "Duck and Weave"},
    "executioner": {"duration": 120, "as_bonus": 10, "label": "Executioner's Stance"},
    "flurry": {"duration": 120, "as_bonus": 6, "label": "Flurry of Blows"},
    "griffin": {"duration": 120, "td_bonus": 10, "label": "Griffin's Voice"},
    "iharmony": {"duration": 120, "ds_bonus": 8, "label": "Inner Harmony"},
    "predator": {"duration": 120, "as_bonus": 10, "label": "Predator's Eye"},
    "krynch": {"duration": 120, "ds_bonus": 10, "label": "Rolling Krynch Stance"},
    "slipperymind": {"duration": 120, "td_bonus": 15, "label": "Slippery Mind"},
    "mongoose": {"duration": 120, "counter_window": True, "label": "Stance of the Mongoose"},
    "asp": {"duration": 120, "as_bonus": 5, "ds_bonus": 5, "label": "Striking Asp Stance"},
}

_ATTACK_PRESETS = {
    "coupdegrace": {"as_bonus": "10 + (5 * rank)", "df_mult": "1.15 + (0.05 * rank)", "crit_bonus": "rank"},
    "exsanguinate": {"as_bonus": "5 + (3 * rank)", "df_mult": "1.0 + (0.08 * rank)", "major_bleed": "max(2, rank + floor(margin / 25))"},
    "leapattack": {"as_bonus": "5 + (3 * rank)", "df_mult": "1.05 + (0.05 * rank)"},
    "mblow": {"df_mult": "1.0 + (0.10 * rank)", "force_target_stance": True},
    "mug": {"as_bonus": "5 + (2 * rank)", "df_mult": "0.95 + (0.04 * rank)", "attempt_steal": True},
    "sattack": {"as_bonus": "rank * 3", "evade_pct_bonus": "rank * 3", "evade_duration": 10},
    "sblow": {"as_bonus": "5 + (2 * rank)", "status": "staggered", "duration": "max(3, floor(margin / 6))"},
    "truestrike": {"ebp_reduce_pct": "rank * 10", "roll_floor": "20 + ((rank - 1) * 10)", "roll_sides": "80 - ((rank - 1) * 10)"},
}

_SETUP_PRESETS = {
    "bash": {"status": "vulnerable", "duration": "15 + (rank * 5)", "extra": ("staggered", "max(3, floor(margin / 5))"), "force_target_stance": True},
    "cpress": {"status": "pressed", "duration": "8 + (rank * 2)"},
    "cutthroat": {"major_bleed": "max(4, rank + floor(damage / 8))", "status": "silenced", "duration": "30 + (rank * 10)", "hidden_required": True},
    "dirtkick": {"status": "blinded", "duration": "5 + floor(margin / 10)", "extra": ("staggered", "max(3, floor(margin / 7))")},
    "disarm": {"status": "staggered", "duration": "max(3, floor(margin / 4))", "disarm": True},
    "dislodge": {"weakened_armament": "15 + (rank * 5)", "pull_weapon": True},
    "divert": {"divert": True, "hidden_required": True},
    "feint": {"ds_bonus": "-(10 + (rank * 5) + max(0, floor(margin / 4)))", "staggered": "max(3, floor(margin / 6))", "force_target_stance": True},
    "footstomp": {"status": "staggered", "duration": "max(3, floor(margin / 6))"},
    "gkick": {"status": "staggered", "duration": "max(3, floor(margin / 8))"},
    "hamstring": {"status": "prone", "duration": "5 + rank", "major_bleed": "max(2, floor(margin / 18))"},
    "haymaker": {"status": "confused", "duration": "5 + (rank * 2)", "extra": ("staggered", "max(3, floor(margin / 10))")},
    "headbutt": {"status": "stunned", "duration": "max(2, rank + floor(margin / 20))", "extra": ("staggered", "max(3, floor(margin / 10))")},
    "kneebash": {"status": "crippled", "duration": "5 + floor(margin / 6)", "magnitude": "max(1, floor(margin / 4))", "extra": ("staggered", "max(3, floor(margin / 6))"), "force_kneel": True},
    "nosetweak": {"status": "demoralized", "duration": "5 + floor(margin / 4)", "magnitude": 20},
    "sbash": {"status": "vulnerable", "duration": "15 + (rank * 5)", "extra": ("staggered", "max(3, floor(margin / 5))"), "force_target_stance": True},
    "scleave": {"strip_spells": "1 if rank < 5 else 2"},
    "spunch": {"status": "silenced", "duration": "rank * 2", "extra": ("staggered", "max(3, floor(margin / 8))"), "force_target_stance": True},
    "subdue": {"status": "stunned", "duration": "max(2, rank + floor(margin / 18))", "extra": ("prone", "5 + rank"), "hidden_required": True},
    "sunder": {"status": "staggered", "duration": "max(3, floor(margin / 5))", "sunder_shield": True},
    "sweep": {"status": "prone", "duration": "5 + rank", "extra": ("vulnerable", "15 + (rank * 5)"), "extra2": ("staggered", "max(3, floor(margin / 6))")},
    "swiftkick": {"status": "staggered", "duration": "max(3, floor(margin / 10))", "force_target_stance": True},
    "tackle": {"status": "prone", "duration": "5 + rank", "extra": ("vulnerable", "15 + (rank * 5)"), "extra2": ("staggered", "3 + floor(margin / 6)")},
    "trip": {"status": "vulnerable", "duration": "15 + (rank * 5)", "extra": ("staggered", "max(3, floor(margin / 7))"), "force_kneel": True},
    "vaultkick": {"status": "dazed", "duration": "15 + (rank * 5)", "extra": ("slowed", "15 + (rank * 5)")},
}

_AOE_PRESETS = {
    "bullrush": {"status": "vulnerable", "duration": "15 + (rank * 5)", "extra": ("staggered", "5 + floor(margin / 6)")},
    "eviscerate": {"major_bleed": "max(2, rank + floor(damage / 10))", "witness_status": "terrified", "witness_duration": 15},
}


def _combat_defs(server) -> dict:
    lua = getattr(server, "lua", None)
    if not lua:
        return {}
    return lua.get_combat_maneuvers() or {}


def _normalize_token(raw: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(raw or "").strip().lower())


def _resolve_mnemonic(server, raw: str) -> tuple[str, dict] | tuple[None, None]:
    defs = _combat_defs(server)
    token = _normalize_token(raw)
    if not token:
        return None, None
    token = _SPECIAL_ALIASES.get(token, token)
    if token in defs and isinstance(defs[token], dict):
        return token, defs[token]
    for mnemonic, meta in defs.items():
        if str(mnemonic).startswith("_") or not isinstance(meta, dict):
            continue
        if _normalize_token(meta.get("name") or mnemonic) == token:
            return str(meta.get("mnemonic") or mnemonic).strip().lower(), meta
    return None, None


def _guild_skill_rank(session, skill_name: str) -> int:
    rows = getattr(session, "guild_skills", {}) or {}
    row = rows.get(skill_name) or {}
    ranks = int(row.get("ranks", 0) or 0) if isinstance(row, dict) else int(row or 0)
    if ranks > 0:
        return ranks
    unlock_key = _GUILD_INTRO_UNLOCKS.get(str(skill_name or "").strip())
    if unlock_key and has_unlock(session, unlock_key):
        return 1
    return 0


def _guild_skill_tier(session, skill_name: str) -> int:
    ranks = _guild_skill_rank(session, skill_name)
    if ranks <= 0:
        return 0
    if ranks >= 54:
        return 5
    if ranks >= 42:
        return 4
    if ranks >= 30:
        return 3
    if ranks >= 20:
        return 2
    return 1


def _effective_maneuver_rank(session, mnemonic: str, meta: dict | None = None) -> int:
    canonical = str(mnemonic or "").strip().lower()
    learned = getattr(session, "combat_maneuvers", {}) or {}
    direct = int(learned.get(canonical, 0) or 0)
    if direct > 0:
        return direct

    if meta:
        unlock_skill = str(meta.get("guild_unlock_skill") or "").strip()
        unlock_rank = int(meta.get("guild_unlock_rank", 0) or 0)
        granted_rank = max(1, int(meta.get("granted_rank", 1) or 1))
        if unlock_skill and unlock_rank > 0:
            if _guild_skill_rank(session, unlock_skill) >= unlock_rank:
                return granted_rank
            return 0

    guild_skill_name = _GUILD_SKILL_NAME_BY_MNEMONIC.get(canonical)
    if guild_skill_name:
        if canonical in {"berserk", "disarm", "feint", "sattack", "stance", "stunman", "subdue", "sweep", "tackle"}:
            return _guild_skill_tier(session, guild_skill_name)
        ranks = _guild_skill_rank(session, guild_skill_name)
        return 1 if ranks > 0 else 0

    if meta and meta.get("is_guild_skill"):
        return 0
    return 0


def _profession_allowed(session, server, meta: dict) -> bool:
    available_to = [str(v).strip().lower() for v in (meta.get("available_to") or []) if str(v or "").strip()]
    if not available_to:
        return True
    return _resolve_profession_name(session, server) in available_to


def _prune_temp_bonuses(session):
    bonuses = []
    now = time.monotonic()
    for row in (getattr(session, "combat_maneuver_bonuses", None) or []):
        if not isinstance(row, dict):
            continue
        expires = float(row.get("expires_at", 0) or 0)
        if expires and expires <= now:
            continue
        bonuses.append(row)
    session.combat_maneuver_bonuses = bonuses
    return bonuses


def add_temp_combat_bonus(session, bonus_id: str, duration: float, **values):
    bonuses = list(_prune_temp_bonuses(session))
    expires_at = time.monotonic() + max(0.0, float(duration or 0))
    bonuses = [row for row in bonuses if str(row.get("id") or "") != str(bonus_id)]
    payload = {"id": str(bonus_id), "expires_at": expires_at}
    payload.update(values)
    bonuses.append(payload)
    session.combat_maneuver_bonuses = bonuses


def get_temp_combat_bonus_totals(session) -> dict:
    totals = {
        "as_bonus": 0,
        "ds_bonus": 0,
        "evade_pct_bonus": 0,
        "parry_pct_bonus": 0,
        "block_pct_bonus": 0,
        "smr_def_bonus": 0,
        "strength_bonus": 0,
        "agility_bonus": 0,
        "dexterity_bonus": 0,
        "intuition_bonus": 0,
        "td_bonus": 0,
    }
    for row in _prune_temp_bonuses(session):
        for key in totals:
            totals[key] += int(row.get(key, 0) or 0)
    return totals


def consume_on_attack_bonuses(session):
    bonuses = []
    for row in _prune_temp_bonuses(session):
        if row.get("consume_on_attack"):
            continue
        bonuses.append(row)
    session.combat_maneuver_bonuses = bonuses


def get_passive_combat_mods(session, server) -> dict:
    totals = {
        "as_bonus": 0,
        "ds_bonus": 0,
        "evade_pct_bonus": 0,
        "parry_pct_bonus": 0,
        "block_pct_bonus": 0,
        "smr_def_bonus": 0,
        "td_bonus": 0,
        "hp_bonus": 0,
        "auto_stand": False,
    }
    defs = _combat_defs(server)
    for mnemonic, preset in _PASSIVE_PRESETS.items():
        meta = defs.get(mnemonic) or {}
        rank = _effective_maneuver_rank(session, mnemonic, meta)
        if rank <= 0:
            continue
        totals["as_bonus"] += int(preset.get("as_bonus_per_rank", 0) * rank)
        totals["ds_bonus"] += int(preset.get("ds_bonus_per_rank", 0) * rank)
        totals["evade_pct_bonus"] += int(preset.get("evade_pct_per_rank", 0) * rank)
        totals["parry_pct_bonus"] += int(preset.get("parry_pct_per_rank", 0) * rank)
        totals["block_pct_bonus"] += int(preset.get("block_pct_per_rank", 0) * rank)
        totals["td_bonus"] += int(preset.get("td_bonus_per_rank", 0) * rank)
        totals["hp_bonus"] += int(preset.get("hp_bonus_base", 0) + (preset.get("hp_bonus_per_rank", 0) * rank))
        rank_table = preset.get("smr_def_bonus_by_rank") or []
        if rank_table:
            rank_index = min(rank, len(rank_table) - 1)
            totals["smr_def_bonus"] += int(rank_table[rank_index] or 0)
        if preset.get("auto_stand"):
            totals["auto_stand"] = True
    return totals


def _sync_toughness_bonus(session):
    base_max = int(getattr(session, "health_max", 100) or 100)
    base_field = getattr(session, "_combat_maneuver_base_health_max", None)
    passive = get_passive_combat_mods(session, getattr(session, "server", None))
    if base_field is None:
        base_field = max(base_max - int(passive.get("hp_bonus", 0) or 0), 1)
        session._combat_maneuver_base_health_max = base_field
    new_max = max(1, int(base_field) + int(passive.get("hp_bonus", 0) or 0))
    old_max = int(getattr(session, "health_max", new_max) or new_max)
    session.health_max = new_max
    if getattr(session, "health_current", 0) > new_max:
        session.health_current = new_max
    elif old_max < new_max and getattr(session, "health_current", 0) > 0:
        session.health_current += (new_max - old_max)


def load_combat_maneuvers_for_session(session, db):
    if not hasattr(session, "combat_maneuvers") or session.combat_maneuvers is None:
        session.combat_maneuvers = {}
    if not hasattr(session, "combat_maneuver_settings") or session.combat_maneuver_settings is None:
        session.combat_maneuver_settings = {}
    if not hasattr(session, "combat_maneuver_bonuses") or session.combat_maneuver_bonuses is None:
        session.combat_maneuver_bonuses = []
    if not hasattr(session, "reaction_triggers") or session.reaction_triggers is None:
        session.reaction_triggers = {}

    if not db or not getattr(session, "character_id", None):
        _sync_toughness_bonus(session)
        return

    session.combat_maneuvers = db.load_character_combat_maneuvers(session.character_id) or {}
    session.combat_maneuver_settings = db.load_character_combat_maneuver_settings(session.character_id) or {}
    _sync_toughness_bonus(session)


def save_combat_maneuver_settings_for_session(session, db=None):
    db = db or getattr(getattr(session, "server", None), "db", None)
    if not db or not getattr(session, "character_id", None):
        return False
    settings = dict(getattr(session, "combat_maneuver_settings", {}) or {})
    return bool(db.save_character_combat_maneuver_settings(session.character_id, settings))


def _eval_formula(expr, *, rank=1, margin=0, damage=0):
    if isinstance(expr, (int, float)):
        return expr
    if expr is None:
        return 0
    text = str(expr).strip()
    if not text:
        return 0
    scope = {
        "rank": float(rank),
        "margin": float(margin),
        "damage": float(damage),
        "success_margin": float(margin),
        "floor": math.floor,
    }

    def _walk(node):
        if isinstance(node, ast.Expression):
            return _walk(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in scope:
                return scope[node.id]
            raise ValueError(f"Unsafe name: {node.id}")
        if isinstance(node, ast.BinOp):
            return _BIN_OPS[type(node.op)](_walk(node.left), _walk(node.right))
        if isinstance(node, ast.UnaryOp):
            return _UNARY_OPS[type(node.op)](_walk(node.operand))
        if isinstance(node, ast.Call):
            func = _walk(node.func)
            args = [_walk(arg) for arg in node.args]
            return func(*args)
        raise ValueError(f"Unsupported formula node: {type(node).__name__}")

    for name, func in _SAFE_FUNCS.items():
        scope[name] = func
    parsed = ast.parse(text, mode="eval")
    return _walk(parsed)


def _skill_bonus_from_ranks(ranks: int) -> int:
    ranks = max(0, int(ranks or 0))
    bonus = 0
    for cap, rate in ((10, 5), (10, 4), (10, 3), (10, 2)):
        take = min(ranks, cap)
        bonus += take * rate
        ranks -= take
        if ranks <= 0:
            return bonus
    return bonus + ranks


def _smr_entities(session, creature) -> tuple[SimpleNamespace, SimpleNamespace]:
    player = SimpleNamespace(
        skill_ranks={
            "dodging": _get_skill_ranks(session, "dodging"),
            "combat_maneuvers": _get_skill_ranks(session, "combat_maneuvers"),
            "perception": _get_skill_ranks(session, "perception"),
            "physical_fitness": _get_skill_ranks(session, "physical_fitness"),
            "shield_use": _get_skill_ranks(session, "shield_use"),
            "brawling": _get_skill_ranks(session, "brawling"),
            "edged_weapons": _get_skill_ranks(session, "edged_weapons"),
            "blunt_weapons": _get_skill_ranks(session, "blunt_weapons"),
            "two_handed_weapons": _get_skill_ranks(session, "two_handed_weapons"),
            "ranged_weapons": _get_skill_ranks(session, "ranged_weapons"),
            "polearm_weapons": _get_skill_ranks(session, "polearm_weapons"),
        },
        stats={
            "agility": int(getattr(session, "stat_agility", 50) or 50),
            "dexterity": int(getattr(session, "stat_dexterity", 50) or 50),
            "intuition": int(getattr(session, "stat_intuition", 50) or 50),
            "strength": int(getattr(session, "stat_strength", 50) or 50),
        },
        race_id=int(getattr(session, "race_id", 0) or 0),
        level=int(getattr(session, "level", 1) or 1),
        stance=str(getattr(session, "stance", "neutral") or "neutral"),
        smr_off_bonus=0,
        smr_def_bonus=int((get_passive_combat_mods(session, getattr(session, "server", None)).get("smr_def_bonus", 0) or 0) + (get_temp_combat_bonus_totals(session).get("smr_def_bonus", 0) or 0)),
        encumbrance_penalty=0,
        armor_action_penalty=0,
    )
    defender = SimpleNamespace(
        skill_ranks=dict(getattr(creature, "skill_ranks", {}) or {}),
        stats=dict(getattr(creature, "stats", {}) or {}),
        race_id=int(getattr(creature, "race_id", 0) or 0),
        level=int(getattr(creature, "level", 1) or 1),
        stance=str(getattr(creature, "stance", "neutral") or "neutral"),
        smr_off_bonus=0,
        smr_def_bonus=0,
        encumbrance_penalty=0,
        armor_action_penalty=0,
    )
    return player, defender


def _find_target(session, server, target_name: str):
    room = getattr(session, "current_room", None)
    if not room:
        return None
    if target_name:
        return server.creatures.find_creature_in_room(room.id, target_name)
    target = getattr(session, "target", None)
    if target and not getattr(target, "is_dead", False):
        return target
    return None


def _status_apply(server, target, effect_id: str, duration: float, magnitude: float = 1):
    effect = _STATUS_NAME_MAP.get(str(effect_id or "").strip().lower(), str(effect_id or "").strip().lower())
    if not effect or duration <= 0:
        return False
    status = getattr(server, "status", None)
    if status:
        return bool(status.apply(target, effect, duration=float(duration), magnitude=float(magnitude or 1)))
    return False


def _setup_header_line(server, mnemonic: str, creature) -> str:
    target = str(getattr(creature, "full_name", None) or getattr(creature, "name", None) or "the target").strip()
    special = {
        "sweep": f"You sweep {target} off its feet.",
        "subdue": f"You spring in and subdue {target}.",
        "trip": f"You trip {target} and throw it off balance.",
        "kneebash": f"You slam into {target}'s knees.",
        "footstomp": f"You stamp down hard on {target}.",
        "nosetweak": f"You twist {target}'s nose sharply.",
        "templeshot": f"You smack {target} across the temple.",
        "throatchop": f"You drive a chop into {target}'s throat.",
        "eyepoke": f"You jab viciously toward {target}'s eyes.",
    }
    return special.get(str(mnemonic or "").strip().lower(), f"You land {meta_name(mnemonic, server)} on {target}.")


def _spend_stamina(session, server, amount: int) -> bool:
    need = max(0, int(amount or 0))
    if int(getattr(session, "stamina_current", 0) or 0) < need:
        return False
    session.stamina_current = max(0, int(session.stamina_current) - need)
    db = getattr(server, "db", None)
    if db and getattr(session, "character_id", None):
        db.save_character_resources(
            session.character_id,
            session.health_current,
            session.mana_current,
            session.spirit_current,
            session.stamina_current,
            session.silver,
        )
    return True


def _roundtime_from_meta(meta: dict) -> int:
    raw = str(meta.get("roundtime") or "").strip().lower()
    if not raw:
        return 0
    match = re.search(r"(\d+)", raw)
    if match:
        return int(match.group(1))
    return 0


def _stamina_cost_from_meta(meta: dict) -> int:
    raw = str(meta.get("stamina") or "").strip()
    nums = [int(v) for v in re.findall(r"\d+", raw)]
    return nums[0] if nums else 0


def available_maneuver_summaries(session, server) -> list[dict]:
    defs = _combat_defs(server)
    out = []
    for mnemonic, meta in defs.items():
        if str(mnemonic).startswith("_") or not isinstance(meta, dict):
            continue
        canonical = str(meta.get("mnemonic") or mnemonic).strip().lower()
        if canonical != str(mnemonic).strip().lower():
            continue
        rank = _effective_maneuver_rank(session, canonical, meta)
        if rank <= 0:
            continue
        if not _profession_allowed(session, server, meta):
            continue
        out.append(
            {
                "mnemonic": canonical,
                "name": str(meta.get("name") or canonical.title()).strip(),
                "type": str(meta.get("type") or "").strip().lower(),
                "category": str(meta.get("category") or "").strip().lower(),
                "rank": rank,
                "targeting": str(meta.get("targeting") or "none").strip().lower(),
                "description": str(meta.get("description") or "").strip(),
                "stamina": _stamina_cost_from_meta(meta),
                "roundtime": _roundtime_from_meta(meta),
                "ready_rule": meta.get("hotbar_ready") if isinstance(meta.get("hotbar_ready"), dict) else None,
                "hotbar_parent": str(meta.get("hotbar_parent") or "").strip().lower(),
                "hotbar_default_child": str(meta.get("hotbar_default_child") or "").strip().lower(),
                "hotbar_subcommand": str(meta.get("hotbar_subcommand") or "").strip().lower(),
            }
        )
    out.sort(key=lambda row: (row["type"], row["name"]))
    return out


def hotbar_child_maneuver_summaries(session, server, parent_key: str) -> list[dict]:
    defs = _combat_defs(server)
    canonical_parent = str(parent_key or "").strip().lower()
    out = []
    for mnemonic, meta in defs.items():
        if str(mnemonic).startswith("_") or not isinstance(meta, dict):
            continue
        canonical = str(meta.get("mnemonic") or mnemonic).strip().lower()
        if canonical != str(mnemonic).strip().lower():
            continue
        if str(meta.get("hotbar_parent") or "").strip().lower() != canonical_parent:
            continue
        if not _profession_allowed(session, server, meta):
            continue
        unlock_skill = str(meta.get("guild_unlock_skill") or "").strip()
        unlock_rank = int(meta.get("guild_unlock_rank", 0) or 0)
        effective_rank = _effective_maneuver_rank(session, canonical, meta)
        out.append(
            {
                "mnemonic": canonical,
                "name": str(meta.get("name") or canonical.title()).strip(),
                "targeting": str(meta.get("targeting") or "none").strip().lower(),
                "effective_rank": effective_rank,
                "unlocked": effective_rank > 0,
                "guild_unlock_skill": unlock_skill,
                "guild_unlock_rank": unlock_rank,
                "granted_rank": max(1, int(meta.get("granted_rank", 1) or 1)),
            }
        )
    out.sort(
        key=lambda row: (
            0 if row["unlocked"] else 1,
            int(row.get("guild_unlock_rank", 0) or 0),
            row["name"],
        )
    )
    return out


def combat_maneuver_ready_state(session, server, mnemonic: str, *, target=None, meta: dict | None = None, rank: int | None = None) -> dict:
    meta = meta or ((_combat_defs(server) or {}).get(mnemonic) or {})
    rule = meta.get("hotbar_ready")
    if not isinstance(rule, dict):
        return {"has_rule": False, "ready": False, "ready_until": None, "message": ""}
    if rank is None:
        rank = _effective_maneuver_rank(session, mnemonic, meta)
    result = evaluate_ready_rule(rule, session=session, server=server, target=target, rank=int(rank or 0))
    result["has_rule"] = True
    return result


def maybe_auto_stand_before_attack(session, server) -> bool:
    passive = get_passive_combat_mods(session, server)
    if not passive.get("auto_stand"):
        return False
    if str(getattr(session, "position", "standing") or "standing") == "standing":
        return False
    status = getattr(server, "status", None)
    blocked = any(status and status.has(session, effect) for effect in ("stunned", "webbed", "rooted", "immobile"))
    if blocked:
        return False
    session.position = "standing"
    if status:
        for effect in ("sitting", "kneeling", "resting", "prone"):
            status.remove(session, effect)
    return True


def _spent_cman_points(session, server) -> int:
    defs = _combat_defs(server)
    total = 0
    for mnemonic, rank in (getattr(session, "combat_maneuvers", {}) or {}).items():
        meta = defs.get(mnemonic) or {}
        costs = [int(v or 0) for v in (meta.get("rank_costs") or [])]
        for idx in range(min(int(rank or 0), len(costs))):
            total += costs[idx]
    return total


def _available_cman_points(session, server) -> int:
    cm_ranks = _get_skill_ranks(session, "combat_maneuvers")
    return max(0, int(cm_ranks or 0) - _spent_cman_points(session, server))


async def _send_cman_list(session, server):
    rows = available_maneuver_summaries(session, server)
    if not rows:
        await session.send_line("You have no combat maneuvers available right now.")
        return
    available_points = _available_cman_points(session, server)
    await session.send_line(f"Combat Maneuvers: {len(rows)} available. CMAN points free: {available_points}.")
    grouped = {}
    for row in rows:
        grouped.setdefault(row["type"], []).append(row)
    for key in ("passive", "buff", "martial_stance", "setup", "attack", "aoe", "concentration"):
        bucket = grouped.get(key) or []
        if not bucket:
            continue
        labels = [f"{row['name']} [{row['mnemonic']}] r{row['rank']}" for row in bucket]
        await session.send_line(f"  {key.replace('_', ' ').title()}: " + ", ".join(labels))


async def _send_cman_info(session, server, mnemonic: str, meta: dict):
    rank = _effective_maneuver_rank(session, mnemonic, meta)
    costs = [int(v or 0) for v in (meta.get("rank_costs") or []) if int(v or 0) > 0]
    await session.send_line(f"{meta.get('name', mnemonic)} [{mnemonic}]")
    await session.send_line(f"  Type: {meta.get('type', 'unknown')}  Rank: {rank}/{meta.get('max_rank', 1)}  Targeting: {meta.get('targeting', 'none')}")
    await session.send_line(f"  Stamina: {meta.get('stamina', '') or 'n/a'}  Roundtime: {meta.get('roundtime', '') or 'n/a'}")
    if costs:
        await session.send_line("  Rank Costs: " + ", ".join(str(v) for v in costs))
    desc = str(meta.get("description") or "").strip()
    if desc:
        await session.send_line("  " + desc)
    mechanics = str(meta.get("mechanics") or "").strip()
    if mechanics:
        await session.send_line("  " + mechanics)


def learn_combat_maneuver_rank(session, server, mnemonic: str, meta: dict | None = None) -> tuple[bool, str]:
    meta = meta or (_combat_defs(server).get(mnemonic) or {})
    if not meta:
        return False, "That is not a known combat maneuver."
    if meta.get("is_guild_skill"):
        return False, "Guild maneuvers are trained through the guild system, not CMAN points."
    if not meta.get("is_learnable", True):
        return False, "That maneuver cannot be learned this way."
    if not _profession_allowed(session, server, meta):
        return False, "Your profession cannot learn that maneuver."

    current = int((getattr(session, "combat_maneuvers", {}) or {}).get(mnemonic, 0) or 0)
    max_rank = int(meta.get("max_rank", 1) or 1)
    if current >= max_rank:
        return False, "You have already mastered that maneuver."

    costs = [int(v or 0) for v in (meta.get("rank_costs") or [])]
    next_cost = costs[current] if current < len(costs) else 0
    if next_cost <= 0:
        return False, "That maneuver has no learnable next rank."

    available = _available_cman_points(session, server)
    if next_cost > available:
        return False, f"You need {next_cost} CMAN points but only have {available} free."

    db = getattr(server, "db", None)
    if not db or not getattr(session, "character_id", None):
        return False, "Combat maneuver training is unavailable right now."
    if not db.save_character_combat_maneuver_rank(session.character_id, mnemonic, current + 1):
        return False, "The training ledger refuses to record that maneuver rank."

    session.combat_maneuvers = dict(getattr(session, "combat_maneuvers", {}) or {})
    session.combat_maneuvers[mnemonic] = current + 1
    _sync_toughness_bonus(session)
    return True, f"You train {meta.get('name', mnemonic)} to rank {current + 1}."


def unlearn_combat_maneuver_rank(session, server, mnemonic: str, meta: dict | None = None) -> tuple[bool, str]:
    meta = meta or (_combat_defs(server).get(mnemonic) or {})
    if not meta:
        return False, "That is not a known combat maneuver."
    if meta.get("is_guild_skill"):
        return False, "Guild maneuvers are removed through guild re-training, not CMAN unlearn."

    current = int((getattr(session, "combat_maneuvers", {}) or {}).get(mnemonic, 0) or 0)
    if current <= 0:
        return False, "You have not learned that maneuver."

    db = getattr(server, "db", None)
    if not db or not getattr(session, "character_id", None):
        return False, "Combat maneuver training is unavailable right now."

    ok = (
        db.save_character_combat_maneuver_rank(session.character_id, mnemonic, current - 1)
        if current > 1
        else db.remove_character_combat_maneuver(session.character_id, mnemonic)
    )
    if not ok:
        return False, "The training ledger refuses to remove that maneuver rank."

    session.combat_maneuvers = dict(getattr(session, "combat_maneuvers", {}) or {})
    if current > 1:
        session.combat_maneuvers[mnemonic] = current - 1
    else:
        session.combat_maneuvers.pop(mnemonic, None)
    _sync_toughness_bonus(session)
    return True, f"You untrain {meta.get('name', mnemonic)} to rank {max(0, current - 1)}."


async def _handle_cman_learn(session, server, mnemonic: str, meta: dict):
    _, message = learn_combat_maneuver_rank(session, server, mnemonic, meta)
    await session.send_line(message)


async def _handle_cman_unlearn(session, server, mnemonic: str, meta: dict):
    _, message = unlearn_combat_maneuver_rank(session, server, mnemonic, meta)
    await session.send_line(message)


async def handle_cman_command(session, cmd: str, args: str, server):
    raw_cmd = str(cmd or "").strip().lower()
    raw_args = str(args or "").strip()

    if raw_cmd == "cman":
        if not raw_args:
            await _send_cman_list(session, server)
            return
        first, _, remainder = raw_args.partition(" ")
        token = first.strip().lower()
        if token in {"list", "all"}:
            await _send_cman_list(session, server)
            return
        if token == "info":
            mnemonic, meta = _resolve_mnemonic(server, remainder)
            if not mnemonic:
                await session.send_line("CMAN INFO requires a known maneuver.")
                return
            await _send_cman_info(session, server, mnemonic, meta)
            return
        if token == "learn":
            mnemonic, meta = _resolve_mnemonic(server, remainder)
            if not mnemonic:
                await session.send_line("CMAN LEARN requires a known maneuver.")
                return
            await _handle_cman_learn(session, server, mnemonic, meta)
            return
        if token == "unlearn":
            mnemonic, meta = _resolve_mnemonic(server, remainder)
            if not mnemonic:
                await session.send_line("CMAN UNLEARN requires a known maneuver.")
                return
            await _handle_cman_unlearn(session, server, mnemonic, meta)
            return
        raw_cmd = token
        raw_args = remainder.strip()

    mnemonic, meta = _resolve_mnemonic(server, raw_cmd)
    if not mnemonic:
        await session.send_line("That is not a known combat maneuver.")
        return
    status = getattr(server, "status", None)
    if status and status.has(session, "revival_shroud"):
        await session.send_line("You are still wrapped in revival starlight and cannot use combat maneuvers yet.")
        return
    await execute_combat_maneuver(session, mnemonic, raw_args, server, meta=meta)


def _best_weapon_skill_ranks(session) -> int:
    hands = [getattr(session, "right_hand", None), getattr(session, "left_hand", None)]
    ranks = [_get_skill_ranks(session, "brawling")]
    mapping = {
        "edged": "edged_weapons",
        "blunt": "blunt_weapons",
        "twohanded": "two_handed_weapons",
        "two_handed": "two_handed_weapons",
        "ranged": "ranged_weapons",
        "polearm": "polearm_weapons",
        "brawling": "brawling",
    }
    for item in hands:
        if not item or item.get("item_type") != "weapon":
            continue
        category = str(item.get("weapon_category") or item.get("weapon_type") or "").strip().lower()
        skill_key = mapping.get(category)
        if skill_key:
            ranks.append(_get_skill_ranks(session, skill_key))
    return max(ranks or [0])


def _shift_target_stance_more_offensive(target):
    order = ["defensive", "guarded", "neutral", "forward", "advance", "offensive"]
    current = str(getattr(target, "stance", "neutral") or "neutral").lower()
    if current not in order:
        current = "neutral"
    idx = order.index(current)
    target.stance = order[min(len(order) - 1, idx + 1)]


def _maneuver_roll(session, creature, rank: int, *, off_bonus=0, def_bonus=0) -> dict:
    player, defender = _smr_entities(session, creature)
    return smr_roll(
        player,
        defender,
        {
            "weapon_skill_ranks": _best_weapon_skill_ranks(session),
            "include_shield": True,
            "use_racial_size": True,
            "attacker_mk_rank": max(0, min(5, int(rank or 0))),
            "defender_mk_rank": max(0, min(5, int(_effective_maneuver_rank(session, "cdefense") or 0))),
            "off_bonus": int(off_bonus or 0),
            "def_bonus": int(def_bonus or 0),
        },
    )


def _apply_strip_spells(target, count: int):
    count = max(0, int(count or 0))
    active = getattr(target, "active_spells", None)
    if not isinstance(active, dict) or count <= 0:
        return 0
    removed = 0
    for spell_id in list(active.keys())[:count]:
        active.pop(spell_id, None)
        removed += 1
    return removed


def _try_disarm_target(target):
    if hasattr(target, "disarmed"):
        target.disarmed = True
        return True
    return False


def _apply_damage_direct(target, amount: int) -> int:
    damage = max(0, int(amount or 0))
    if damage <= 0:
        return 0
    if hasattr(target, "take_damage"):
        return int(target.take_damage(damage) or 0)
    current = int(getattr(target, "health_current", 0) or 0)
    target.health_current = max(0, current - damage)
    return damage


def _mark_maneuver_used(session, server, mnemonic: str):
    db = getattr(server, "db", None)
    if db and getattr(session, "character_id", None):
        db.touch_character_combat_maneuver_used(session.character_id, mnemonic)


async def _use_buff_maneuver(session, server, mnemonic: str, rank: int):
    preset = _BUFF_PRESETS.get(mnemonic, {})
    label = preset.get("label") or mnemonic.title()
    if "heal" in preset:
        heal = int(_eval_formula(preset.get("heal"), rank=rank) or 0)
        session.health_current = min(int(getattr(session, "health_max", 100) or 100), int(getattr(session, "health_current", 0) or 0) + heal)
        await session.send_line(f"You draw inward and restore {heal} health.")
        return
    duration = float(_eval_formula(preset.get("duration", 90), rank=rank) or 0)
    bonus_id = f"cman:{mnemonic}"
    values = {}
    for key in ("strength_bonus", "agility_bonus", "dexterity_bonus", "intuition_bonus", "as_bonus", "ds_bonus", "td_bonus"):
        if key not in preset:
            continue
        values[key] = int(_eval_formula(preset.get(key), rank=rank) or 0)
    if preset.get("consume_on_attack"):
        values["consume_on_attack"] = True
    add_temp_combat_bonus(session, bonus_id, duration, **values)
    if preset.get("status"):
        magnitude = float(_eval_formula(preset.get("magnitude", 1), rank=rank) or 1)
        _status_apply(server, session, preset["status"], float(_eval_formula(preset.get("duration", duration), rank=rank) or duration), magnitude=magnitude)
    if preset.get("hide"):
        session.hidden = True
    await session.send_line(f"You settle into {label}.")


async def _use_stance_maneuver(session, server, mnemonic: str, rank: int):
    preset = _STANCE_PRESETS.get(mnemonic, {})
    label = preset.get("label") or mnemonic.title()
    add_temp_combat_bonus(
        session,
        f"cman-stance:{mnemonic}",
        float(preset.get("duration", 120) or 120),
        as_bonus=int(preset.get("as_bonus", 0) or 0),
        ds_bonus=int(preset.get("ds_bonus", 0) or 0),
        td_bonus=int(preset.get("td_bonus", 0) or 0),
        evade_pct_bonus=int(preset.get("evade_pct_bonus", 0) or 0),
        counter_window=bool(preset.get("counter_window")),
        stance_maneuver=mnemonic,
    )
    await session.send_line(f"You settle into {label}.")


async def _apply_setup_effects(session, server, creature, spec: dict, *, rank: int, margin: int, damage: int = 0):
    applied: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def note(effect_id: str, *, target_label: str = "defender"):
        key = (str(effect_id or "").strip().lower(), str(target_label or "defender").strip().lower())
        if key in seen:
            return
        seen.add(key)
        applied.append({
            "effect": effect_id,
            "entity": creature if target_label == "defender" else session,
            "target_label": target_label,
        })

    if spec.get("status"):
        duration = float(_eval_formula(spec.get("duration", 5), rank=rank, margin=margin, damage=damage) or 0)
        magnitude = float(_eval_formula(spec.get("magnitude", 1), rank=rank, margin=margin, damage=damage) or 1)
        _status_apply(server, creature, spec["status"], duration, magnitude=magnitude)
        note(spec["status"])
    for extra_key in ("extra", "extra2"):
        payload = spec.get(extra_key)
        if not payload:
            continue
        effect_id, duration_expr = payload
        _status_apply(server, creature, effect_id, float(_eval_formula(duration_expr, rank=rank, margin=margin, damage=damage) or 0))
        note(effect_id)
    if spec.get("staggered"):
        _status_apply(server, creature, "staggered", float(_eval_formula(spec["staggered"], rank=rank, margin=margin, damage=damage) or 0))
        note("staggered")
    if spec.get("major_bleed"):
        magnitude = float(_eval_formula(spec["major_bleed"], rank=rank, margin=margin, damage=damage) or 1)
        _status_apply(server, creature, "major_bleed", 30, magnitude=magnitude)
        note("major_bleed")
    if spec.get("weakened_armament"):
        magnitude = float(_eval_formula(spec["weakened_armament"], rank=rank, margin=margin, damage=damage) or 1)
        _status_apply(server, creature, "weakened_armament", 30, magnitude=magnitude)
        note("weakened_armament")
    if spec.get("ds_bonus") and hasattr(creature, "apply_temporary_bonus"):
        ds_bonus = int(_eval_formula(spec["ds_bonus"], rank=rank, margin=margin, damage=damage) or 0)
        creature.apply_temporary_bonus(f"cman:{id(spec)}", 15, ds_bonus=ds_bonus)
        applied.append({"effect": "ds_bonus", "entity": creature, "target_label": "defender"})
    if spec.get("force_target_stance"):
        _shift_target_stance_more_offensive(creature)
    if spec.get("force_kneel"):
        _status_apply(server, creature, "prone", 4)
        note("prone")
    if spec.get("disarm"):
        _try_disarm_target(creature)
        applied.append({"effect": "weakened_armament", "entity": creature, "target_label": "defender"})
    if spec.get("strip_spells"):
        count = int(_eval_formula(spec["strip_spells"], rank=rank, margin=margin, damage=damage) or 0)
        _apply_strip_spells(creature, count)
        if count > 0:
            applied.append({"effect": "disoriented", "entity": creature, "target_label": "defender"})
    return applied


async def _use_attack_maneuver(session, server, mnemonic: str, creature, rank: int, meta: dict):
    preset = _ATTACK_PRESETS.get(mnemonic, {})
    applied: list[dict] = []
    status = getattr(server, "status", None)
    if preset.get("need_vulnerable") and not (status and status.has(creature, "vulnerable")):
        await session.send_line("That maneuver requires a vulnerable target.")
        return False
    if mnemonic == "sattack":
        duration = int(preset.get("evade_duration", 10) or 10)
        add_temp_combat_bonus(
            session,
            "cman:sattack:evade",
            duration,
            evade_pct_bonus=int(_eval_formula(preset.get("evade_pct_bonus", 0), rank=rank) or 0),
        )
    context = {
        "mnemonic": mnemonic,
        "rank": rank,
        "as_bonus": int(_eval_formula(preset.get("as_bonus", 0), rank=rank) or 0),
        "df_mult": float(_eval_formula(preset.get("df_mult", 1.0), rank=rank) or 1.0),
        "crit_phantom": int(_eval_formula(preset.get("crit_bonus", 0), rank=rank) or 0),
        "force_target_stance": bool(preset.get("force_target_stance")),
        "ebp_reduce_pct": int(_eval_formula(preset.get("ebp_reduce_pct", 0), rank=rank) or 0),
        "roll_floor": int(_eval_formula(preset.get("roll_floor", 0), rank=rank) or 0),
        "roll_sides": int(_eval_formula(preset.get("roll_sides", 0), rank=rank) or 0),
        "roundtime_modifier": -1 if str(meta.get("roundtime") or "").strip().lower() == "attack-1" else 0,
    }
    session.combat_maneuver_attack_context = context
    session.combat_maneuver_last_attack = None
    await server.combat.player_attacks_creature(session, creature)
    outcome = getattr(session, "combat_maneuver_last_attack", None) or {}
    if not outcome.get("hit"):
        return False
    margin = max(0, int(outcome.get("endroll", 100) or 100) - 100)
    damage = int(outcome.get("damage", 0) or 0)
    if preset.get("status"):
        _status_apply(server, creature, preset["status"], float(_eval_formula(preset.get("duration", 5), rank=rank, margin=margin, damage=damage) or 0))
        applied.append({"effect": preset["status"], "entity": creature, "target_label": "defender"})
    if preset.get("major_bleed"):
        magnitude = float(_eval_formula(preset.get("major_bleed"), rank=rank, margin=margin, damage=damage) or 1)
        _status_apply(server, creature, "major_bleed", 30, magnitude=magnitude)
        applied.append({"effect": "major_bleed", "entity": creature, "target_label": "defender"})
    for line in summarize_applied_effects(server, applied):
        await session.send_line(line)
    if preset.get("attempt_steal") and int(getattr(session, "silver", 0) or 0) >= 0:
        creature_silver = int(getattr(creature, "silver", 0) or 0)
        if creature_silver > 0:
            stolen = max(1, min(creature_silver, 10 + (rank * 10)))
            creature.silver = creature_silver - stolen
            session.silver = int(getattr(session, "silver", 0) or 0) + stolen
            await session.send_line(f"You snatch {stolen} silver from {creature.full_name} in the motion of the attack.")
        else:
            await session.send_line(f"You land the mugging strike, but come away empty-handed from {creature.full_name}.")
    return bool(outcome.get("killed"))


async def _use_setup_maneuver(session, server, mnemonic: str, creature, rank: int):
    spec = _SETUP_PRESETS.get(mnemonic, {})
    roll = _maneuver_roll(session, creature, rank)
    await session.send_line(roll.get("msg") or "[SMR result]")
    if not roll.get("success"):
        await session.send_line(f"You fail to execute {mnemonic} cleanly.")
        return False
    margin = int(roll.get("margin", 0) or 0)
    if spec.get("divert"):
        await session.send_line(f"You divert {creature.full_name} and send it stumbling away!")
        if getattr(server, "status", None) and hasattr(server.status, "_creature_flee"):
            await server.status._creature_flee(creature)
        return False
    damage = 0
    if mnemonic in {"cutthroat", "dislodge", "hamstring", "headbutt", "haymaker", "spunch", "trip", "vaultkick"}:
        damage = _apply_damage_direct(creature, 6 + (rank * 3) + max(0, margin // 8))
        if damage > 0:
            await session.send_line(f"Your maneuver lands for {damage} direct damage.")
    await session.send_line(_setup_header_line(server, mnemonic, creature))
    applied = await _apply_setup_effects(session, server, creature, spec, rank=rank, margin=margin, damage=damage)
    summary_lines = summarize_applied_effects(server, applied)
    if summary_lines:
        for line in summary_lines:
            await session.send_line(line)
    elif damage <= 0:
        await session.send_line(f"{meta_name(mnemonic, server)} lands cleanly, but produces no lasting effect.")
    return bool(getattr(creature, "is_dead", False))


async def _use_aoe_maneuver(session, server, mnemonic: str, primary_target, rank: int):
    spec = _AOE_PRESETS.get(mnemonic, {})
    room_id = getattr(getattr(session, "current_room", None), "id", None)
    creatures = list(getattr(server.creatures, "get_creatures_in_room", lambda _rid: [])(room_id) or [])
    total_hits = 0
    applied: list[dict] = []
    for creature in creatures:
        if getattr(creature, "is_dead", False):
            continue
        roll = _maneuver_roll(session, creature, rank, off_bonus=5 if creature is primary_target else 0)
        if not roll.get("success"):
            continue
        total_hits += 1
        margin = int(roll.get("margin", 0) or 0)
        damage = _apply_damage_direct(creature, 8 + (rank * 4) + max(0, margin // 6))
        applied.extend(await _apply_setup_effects(session, server, creature, spec, rank=rank, margin=margin, damage=damage))
    if mnemonic == "eviscerate":
        for creature in creatures:
            if creature is primary_target or getattr(creature, "is_dead", False):
                continue
            _status_apply(server, creature, spec.get("witness_status", "terrified"), float(spec.get("witness_duration", 15) or 15))
            applied.append({"effect": spec.get("witness_status", "terrified"), "entity": creature, "target_label": "defender"})
    await session.send_line(f"{meta_name(mnemonic, server)} tears through {total_hits} foe(s).")
    for line in summarize_applied_effects(server, applied):
        await session.send_line(line)
    return False


async def _use_concentration_maneuver(session, server, mnemonic: str, creature, rank: int):
    status = getattr(server, "status", None)
    empowered = bool(status and status.has(creature, "vulnerable"))
    rounds = 2 if empowered and mnemonic == "bearhug" else 3 if mnemonic == "bearhug" else 3 if empowered else 4
    damage = 0
    for idx in range(rounds):
        damage += _apply_damage_direct(creature, 6 + (rank * 4) + (idx * 2))
    if mnemonic == "bearhug":
        add_temp_combat_bonus(session, "cman:bearhug:party", 120, strength_bonus=10)
        await session.send_line(f"You crush {creature.full_name} in a brutal bearhug for {damage} damage.")
    else:
        add_temp_combat_bonus(session, "cman:garrote:party", 120, agility_bonus=10)
        await session.send_line(f"You cinch the garrote tight around {creature.full_name} for {damage} damage.")
    return bool(getattr(creature, "is_dead", False))


def meta_name(mnemonic: str, server) -> str:
    meta = (_combat_defs(server) or {}).get(mnemonic) or {}
    return str(meta.get("name") or mnemonic.title()).strip()


async def execute_combat_maneuver(session, mnemonic: str, raw_args: str, server, *, meta: dict | None = None):
    meta = meta or ((_combat_defs(server) or {}).get(mnemonic) or {})
    if not meta:
        await session.send_line("That combat maneuver is unavailable right now.")
        return
    if getattr(session, "is_dead", False):
        await session.send_line("You are dead and cannot execute combat maneuvers.")
        return
    if not _profession_allowed(session, server, meta):
        await session.send_line("Your profession cannot use that maneuver.")
        return
    rank = _effective_maneuver_rank(session, mnemonic, meta)
    if rank <= 0:
        await session.send_line("You have not learned that maneuver.")
        return
    if mnemonic == "cheapshots":
        await session.send_line("Use the individual cheapshot maneuvers directly: FOOTSTOMP, NOSETWEAK, TEMPLESHOT, KNEEBASH, EYEPOKE, THROATCHOP, SWIFTKICK.")
        return
    if mnemonic == "stunman":
        await session.send_line("Use STUNMAN with an action, such as STUNMAN STAND or STUNMAN ATTACK.")
        return
    mtype = str(meta.get("type") or "").strip().lower()
    if mtype == "passive":
        await _send_cman_info(session, server, mnemonic, meta)
        return

    status = getattr(server, "status", None)
    if status and status.has(session, "stunned") and mnemonic not in {"stunman", "berserk"}:
        await session.send_line("You are stunned.")
        return
    if mtype in _ACTIVATABLE_TYPES and str(getattr(session, "position", "standing") or "standing") != "standing":
        if not maybe_auto_stand_before_attack(session, server):
            await session.send_line("You need to stand up first.")
            return

    spec = _SETUP_PRESETS.get(mnemonic, {}) | _ATTACK_PRESETS.get(mnemonic, {}) | _AOE_PRESETS.get(mnemonic, {})
    if spec.get("hidden_required") and not getattr(session, "hidden", False):
        await session.send_line("You need to be hidden first.")
        return

    targeting = str(meta.get("targeting") or "none").strip().lower()
    target_name = raw_args.strip()
    creature = None
    if targeting in {"current_target", "current_target_optional"}:
        creature = _find_target(session, server, target_name)
        if not creature and targeting == "current_target":
            await session.send_line("You need a valid target for that maneuver.")
            return

    ready_state = combat_maneuver_ready_state(
        session,
        server,
        mnemonic,
        target=creature,
        meta=meta,
        rank=rank,
    )
    if ready_state.get("has_rule") and not ready_state.get("ready"):
        await session.send_line(ready_state.get("message") or "You cannot use that maneuver right now.")
        return

    stamina = _stamina_cost_from_meta(meta)
    if not _spend_stamina(session, server, stamina):
        await session.send_line("You are too tired to execute that maneuver.")
        return

    if creature is not None and not getattr(creature, "is_dead", False):
        session.target = creature
        session.in_combat = True
        setattr(creature, "target", session)
        setattr(creature, "in_combat", True)

    broke_hidden = False
    if getattr(session, "hidden", False) and mtype in {"attack", "setup", "aoe", "concentration"}:
        session.hidden = False
        broke_hidden = True

    rt = _roundtime_from_meta(meta)
    killed = False
    if mtype == "buff":
        await _use_buff_maneuver(session, server, mnemonic, rank)
    elif mtype == "martial_stance":
        await _use_stance_maneuver(session, server, mnemonic, rank)
    elif mtype == "attack":
        killed = await _use_attack_maneuver(session, server, mnemonic, creature, rank, meta)
    elif mtype == "setup":
        killed = await _use_setup_maneuver(session, server, mnemonic, creature, rank)
    elif mtype == "aoe":
        killed = await _use_aoe_maneuver(session, server, mnemonic, creature, rank)
    elif mtype == "concentration":
        killed = await _use_concentration_maneuver(session, server, mnemonic, creature, rank)
    else:
        await session.send_line(f"{meta_name(mnemonic, server)} has no executable runtime yet.")

    if rt > 0 and session.get_roundtime() < rt:
        session.set_roundtime(rt)
        await session.send_line(roundtime_msg(rt))
    if broke_hidden:
        await session.send_line(colorize("  You slip from hiding as the maneuver unfolds.", TextPresets.SYSTEM))
    _mark_maneuver_used(session, server, mnemonic)
    if killed:
        session.target = None
