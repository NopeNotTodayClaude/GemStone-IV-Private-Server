"""
appearance_loader.py
--------------------
Loads character creation appearance data from scripts/data/appearance.lua.

Returns a dict with keys:
  "hair_colors"       - list of hair color strings
  "hair_styles"       - list of hair style strings
  "eye_colors"        - list of eye color strings
  "skin_tones"        - list of skin tone strings
  "stat_names"        - list of 10 stat name strings
  "stat_abbrevs"      - list of 10 stat abbreviation strings
  "stat_keys"         - list of 10 stat key strings (DB column names)
  "stat_descriptions" - dict {stat_idx (0-based): description}
  "suggested_stats"   - dict {prof_id: [10 stat values]}
  "cultures"          - dict {race_id: {label, options: [{key,name,desc}]}}
  "age_ranges"        - dict {race_id: [[min,max] x 11 stages]}
  "age_stage_names"   - list of 11 stage name strings

Raises RuntimeError on failure. There are no Python fallbacks.
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


def load_appearance(lua_engine) -> Optional[dict]:
    if not lua_engine or not lua_engine.available:
        raise RuntimeError("appearance_loader: Lua engine not available. Check lupa installation and scripts path.")
    try:
        data = lua_engine.load_data("data/appearance")
        if not data:
            raise RuntimeError("appearance_loader: Lua returned no data. Check scripts/data/ for errors.")

        result = {}

        # ── Simple string lists ──────────────────────────────────────────────
        for key in ("hair_colors", "hair_styles", "eye_colors", "skin_tones",
                    "stat_names", "stat_abbrevs", "stat_keys", "age_stage_names"):
            raw = data.get(key)
            if isinstance(raw, list):
                result[key] = [str(v) for v in raw]
            elif isinstance(raw, dict):
                # Lua returns 1-indexed tables as dicts when mixed
                result[key] = [str(raw[i]) for i in sorted(raw.keys())]
            else:
                result[key] = []

        # ── Stat descriptions: Lua 1-based → Python 0-based ─────────────────
        raw_desc = data.get("stat_descriptions") or {}
        stat_desc = {}
        if isinstance(raw_desc, dict):
            for k, v in raw_desc.items():
                stat_desc[int(k) - 1] = str(v)  # convert 1-based Lua to 0-based Python
        result["stat_descriptions"] = stat_desc

        # ── Suggested stats: {prof_id: [10 values]} ──────────────────────────
        raw_sug = data.get("suggested_stats") or {}
        suggested = {}
        if isinstance(raw_sug, dict):
            for prof_id, vals in raw_sug.items():
                if isinstance(vals, (list, dict)):
                    if isinstance(vals, dict):
                        vals = [vals[i] for i in sorted(vals.keys())]
                    suggested[int(prof_id)] = [int(v) for v in vals]
        result["suggested_stats"] = suggested

        # ── Cultures: {race_id: {label, options}} ────────────────────────────
        raw_cult = data.get("cultures") or {}
        cultures = {}
        if isinstance(raw_cult, dict):
            for race_id, block in raw_cult.items():
                if isinstance(block, dict):
                    label = str(block.get("label", ""))
                    raw_opts = block.get("options") or []
                    options = []
                    if isinstance(raw_opts, (list, dict)):
                        if isinstance(raw_opts, dict):
                            raw_opts = [raw_opts[i] for i in sorted(raw_opts.keys())]
                        for opt in raw_opts:
                            if isinstance(opt, dict):
                                options.append({
                                    "key":  str(opt.get("key", "")),
                                    "name": str(opt.get("name", "")),
                                    "desc": str(opt.get("desc", "")),
                                })
                    cultures[int(race_id)] = {"label": label, "options": options}
        result["cultures"] = cultures

        # ── Age ranges: {race_id: [[min,max] x 11]} ──────────────────────────
        raw_ages = data.get("age_ranges") or {}
        age_ranges = {}
        if isinstance(raw_ages, dict):
            for race_id, stages in raw_ages.items():
                if isinstance(stages, (list, dict)):
                    if isinstance(stages, dict):
                        stages = [stages[i] for i in sorted(stages.keys())]
                    parsed = []
                    for stage in stages:
                        if isinstance(stage, (list, dict)):
                            if isinstance(stage, dict):
                                stage = [stage[i] for i in sorted(stage.keys())]
                            parsed.append([int(stage[0]), int(stage[1])])
                    age_ranges[int(race_id)] = parsed
        result["age_ranges"] = age_ranges

        log.info(
            "appearance_loader: loaded %d hair colors, %d cultures, %d age race tables",
            len(result.get("hair_colors", [])),
            len(result.get("cultures", {})),
            len(result.get("age_ranges", {})),
        )
        return result

    except RuntimeError:
        raise
    except Exception as e:
        log.critical("appearance_loader: failed to load Lua data: %s", e, exc_info=True)
        raise RuntimeError(f"appearance_loader: Lua load failed — {e}") from e
