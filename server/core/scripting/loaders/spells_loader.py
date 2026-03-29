"""
spells_loader.py
----------------
Seeds the spells table by calling .seed() on each spell-circle Lua module
at server startup.

Each module under scripts/spells/<circle>.lua must export:
    seed()     -- INSERTs / upserts that circle's rows into `spells`
    on_cast(ctx) -- dispatches to per-spell handlers (called by spell_engine)

Usage (called from LuaManager.seed_spells):
    load_spells(lua_engine)

Returns: dict of { circle_name: spell_count } for logging.
Raises RuntimeError on any critical failure.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

# Trainable circles first; non-trainable stubs last.
SPELL_CIRCLE_MODULES = [
    # (module_path,            circle_name,        circle_id)
    ("spells/minor_spiritual", "Minor Spiritual",  1),
    ("spells/major_spiritual", "Major Spiritual",  2),
    ("spells/cleric",          "Cleric Base",      3),
    ("spells/minor_elemental", "Minor Elemental",  4),
    ("spells/major_elemental", "Major Elemental",  5),
    ("spells/ranger",          "Ranger Base",      6),
    ("spells/sorcerer",        "Sorcerer Base",    7),
    ("spells/wizard",          "Wizard Base",      8),
    ("spells/bard",            "Bard Base",        9),
    ("spells/empath",          "Empath Base",      10),
    ("spells/paladin",         "Paladin Base",     11),
    ("spells/minor_mental",    "Minor Mental",     12),
    ("spells/major_mental",    "Major Mental",     13),
    ("spells/savant",          "Savant Base",      14),
    ("spells/arcane",          "Arcane",           15),
    ("spells/pet_companions",  "Pet Companions",   15),
]


def load_spells(lua_engine) -> Optional[dict]:
    """
    Call seed() on every registered circle module.
    Returns a summary dict or None if engine is unavailable.
    """
    if not lua_engine or not lua_engine.available:
        raise RuntimeError(
            "spells_loader: Lua engine not available. "
            "Check lupa installation and scripts path."
        )

    summary = {}
    errors  = []

    for module_path, circle_name, circle_id in SPELL_CIRCLE_MODULES:
        try:
            mod = lua_engine.require(module_path)
            if mod is None:
                raise RuntimeError(f"require('{module_path}') returned nil")

            # Call seed() — each circle module handles its own upserts.
            seed_fn = getattr(mod, "seed", None)
            if seed_fn is None:
                raise RuntimeError(
                    f"Module '{module_path}' missing seed() function"
                )
            seed_fn()

            # Ask the DB how many spells we actually have for this circle.
            count_result = lua_engine.execute(
                f"return require('globals/utils/db')"
                f".queryOne('SELECT COUNT(*) as n FROM spells WHERE circle_id={circle_id}')"
            )
            count = 0
            if count_result and hasattr(count_result, "__getitem__"):
                try:
                    count = int(count_result["n"] or 0)
                except Exception:
                    pass

            summary[circle_name] = count
            log.info(
                "spells_loader: seeded circle %d (%s) — %d spell(s)",
                circle_id, circle_name, count
            )

        except Exception as e:
            errors.append(f"{circle_name}: {e}")
            log.error(
                "spells_loader: failed to seed %s (circle_id=%d): %s",
                circle_name, circle_id, e, exc_info=True
            )

    if errors:
        # Non-fatal: log everything but keep the server alive.
        log.warning(
            "spells_loader: %d circle(s) failed to seed:\n  %s",
            len(errors), "\n  ".join(errors)
        )

    total = sum(summary.values())
    log.info("spells_loader: total spells in DB after seed: %d", total)
    return summary
