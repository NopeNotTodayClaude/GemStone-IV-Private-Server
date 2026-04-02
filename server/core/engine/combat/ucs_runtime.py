"""
ucs_runtime.py
--------------
Shared UCS tuning state loaded from scripts/globals/ucs.lua.

This keeps unarmed ratio/MM/fallback-UDF behavior centralized so creatures,
NPCs, and the combat engine all use the same numbers.
"""

from __future__ import annotations

from copy import deepcopy

_DEFAULTS = {
    "ratio_cap": 2.0,
    "stance_mm": {
        "offensive": 100,
        "advance": 90,
        "forward": 80,
        "neutral": 70,
        "guarded": 55,
        "defensive": 40,
    },
    "fallback_udf": {
        "minimum": 1,
        "melee_ds_multiplier": 1.0,
        "level_bonus_multiplier": 2.0,
        "flat_bonus": 0,
    },
}

_CFG = deepcopy(_DEFAULTS)


def configure_ucs(cfg: dict | None) -> dict:
    """Replace the live UCS config with Lua-loaded values merged over defaults."""
    global _CFG
    merged = deepcopy(_DEFAULTS)
    if isinstance(cfg, dict):
        if "ratio_cap" in cfg:
            try:
                merged["ratio_cap"] = float(cfg.get("ratio_cap", merged["ratio_cap"]))
            except (TypeError, ValueError):
                pass
        stance_mm = cfg.get("stance_mm")
        if isinstance(stance_mm, dict):
            for key, default_val in merged["stance_mm"].items():
                try:
                    merged["stance_mm"][key] = int(stance_mm.get(key, default_val))
                except (TypeError, ValueError):
                    pass
        fallback_udf = cfg.get("fallback_udf")
        if isinstance(fallback_udf, dict):
            for key, default_val in merged["fallback_udf"].items():
                raw = fallback_udf.get(key, default_val)
                try:
                    merged["fallback_udf"][key] = (
                        float(raw) if isinstance(default_val, float) else int(raw)
                    )
                except (TypeError, ValueError):
                    pass
    _CFG = merged
    return deepcopy(_CFG)


def get_ucs_cfg() -> dict:
    return deepcopy(_CFG)


def get_ucs_ratio_cap() -> float:
    try:
        return max(0.1, float(_CFG.get("ratio_cap", 2.0)))
    except (TypeError, ValueError):
        return 2.0


def get_ucs_mm_for_stance(stance: str | None) -> int:
    stance_key = str(stance or "neutral").strip().lower()
    table = _CFG.get("stance_mm", {}) or {}
    try:
        return int(table.get(stance_key, table.get("neutral", 70)))
    except (TypeError, ValueError):
        return 70


def derive_fallback_udf(level: int, melee_ds: int) -> int:
    """
    Derive a sane UDF when a template leaves udf at 0.

    Uses melee DS plus a level bonus, matching the shared Lua config instead of
    reusing raw melee DS as the entire defender factor.
    """
    cfg = _CFG.get("fallback_udf", {}) or {}
    try:
        minimum = int(cfg.get("minimum", 1))
    except (TypeError, ValueError):
        minimum = 1
    try:
        ds_mult = float(cfg.get("melee_ds_multiplier", 1.0))
    except (TypeError, ValueError):
        ds_mult = 1.0
    try:
        level_mult = float(cfg.get("level_bonus_multiplier", 2.0))
    except (TypeError, ValueError):
        level_mult = 2.0
    try:
        flat_bonus = float(cfg.get("flat_bonus", 0))
    except (TypeError, ValueError):
        flat_bonus = 0.0

    derived = int((max(0, int(melee_ds or 0)) * ds_mult) + (max(0, int(level or 0)) * level_mult) + flat_bonus)
    return max(minimum, derived)
