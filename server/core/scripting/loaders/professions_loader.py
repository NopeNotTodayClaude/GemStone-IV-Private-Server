"""
professions_loader.py
---------------------
Loads profession definitions from scripts/data/professions.lua.

Returns a dict with keys:
  "professions"        - list of {id, name, type, desc}
  "profession_stats"   - {prof_id: {hp, mana}}
  "prime_requisites"   - {prof_id: (stat_idx_a, stat_idx_b)}
  "mana_stats"         - {prof_id: (stat_idx_a, stat_idx_b)}
  "growth_rates"       - {prof_id: [10 values]}

Raises RuntimeError if Lua unavailable or load fails.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def _iter_numeric_mapping(raw):
    if isinstance(raw, dict):
        for k, v in raw.items():
            try:
                yield int(k), v
            except Exception:
                continue
        return
    if isinstance(raw, list):
        for idx, value in enumerate(raw, 1):
            if value is None:
                continue
            yield idx, value


def _load_numeric_pair_map(raw):
    out = {}
    for key, value in _iter_numeric_mapping(raw):
        if isinstance(value, list) and len(value) >= 2:
            out[int(key)] = (int(value[0]), int(value[1]))
    return out


def _load_numeric_list_map(raw):
    out = {}
    for key, value in _iter_numeric_mapping(raw):
        if isinstance(value, list):
            out[int(key)] = [int(x) for x in value]
    return out


def load_professions(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("professions_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/professions")
        if not data:
            raise RuntimeError("professions_loader: Lua returned no data. Check scripts/data/ for errors.")

        professions   = []
        prof_stats    = {}
        prime_reqs    = {}
        mana_stats    = {}
        growth_rates  = {}

        for p in (data.get("list") or []):
            if not isinstance(p, dict):
                continue
            professions.append({
                "id":   int(p.get("id", 0)),
                "name": str(p.get("name", "")),
                "type": str(p.get("type", "square")),
                "desc": str(p.get("desc", "")),
            })

        for k, v in _iter_numeric_mapping(data.get("profession_stats") or {}):
            if isinstance(v, dict):
                prof_stats[int(k)] = {
                    "hp":   int(v.get("hp", 0)),
                    "mana": int(v.get("mana", 0)),
                }

        prime_reqs = _load_numeric_pair_map(data.get("prime_requisites") or {})

        mana_stats = _load_numeric_pair_map(data.get("mana_stats") or {})

        growth_rates = _load_numeric_list_map(data.get("growth_rates") or {})

        log.info("professions_loader: loaded %d professions from Lua", len(professions))
        return {
            "professions":     professions,
            "profession_stats": prof_stats,
            "prime_requisites": prime_reqs,
            "mana_stats":       mana_stats,
            "growth_rates":     growth_rates,
        }
    except RuntimeError:
        raise
    except Exception as e:
        log.critical("professions_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"professions_loader: Lua load failed — {e}") from e
