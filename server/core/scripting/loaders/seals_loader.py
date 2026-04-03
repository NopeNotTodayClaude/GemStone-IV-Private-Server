"""
seals_loader.py
---------------
Loads global seal-award tuning from scripts/globals/seals.lua.
"""

import logging

log = logging.getLogger(__name__)

_DEFAULTS = {
    "enabled": True,
    "defaults": {
        "drop_chance": 0.30,
        "quantity": 1,
        "stack_cap": 999,
        "allowed_sources": ["*"],
        "auto_mark": True,
        "announce": True,
    },
    "seal_types": {},
}


def _merge_defaults(defaults, overrides):
    if not isinstance(defaults, dict):
        return overrides if overrides is not None else defaults
    merged = {}
    overrides = overrides if isinstance(overrides, dict) else {}
    for key, default_val in defaults.items():
        if key in overrides:
            if isinstance(default_val, dict):
                merged[key] = _merge_defaults(default_val, overrides.get(key))
            else:
                merged[key] = overrides.get(key)
        else:
            merged[key] = default_val
    for key, override_val in overrides.items():
        if key not in merged:
            merged[key] = override_val
    return merged


def _normalize_sources(raw):
    if isinstance(raw, (list, tuple, set)):
        return [str(source).strip().lower() for source in raw if str(source).strip()]
    if raw is None:
        return ["*"]
    text = str(raw).strip().lower()
    return [text] if text else ["*"]


def load_seals_cfg(lua_engine) -> dict:
    if not lua_engine or not lua_engine.available:
        log.warning("seals_loader: Lua engine unavailable - using defaults")
        return _merge_defaults(_DEFAULTS, {})

    try:
        data = lua_engine.load_data("globals/seals")
        if not data:
            log.warning("seals_loader: Lua returned no data - using defaults")
            return _merge_defaults(_DEFAULTS, {})

        cfg = _merge_defaults(_DEFAULTS, data)
        defaults = dict(cfg.get("defaults") or {})
        defaults["drop_chance"] = max(0.0, min(1.0, float(defaults.get("drop_chance", 0.30) or 0.30)))
        defaults["quantity"] = max(1, int(defaults.get("quantity", 1) or 1))
        defaults["stack_cap"] = max(1, int(defaults.get("stack_cap", 999) or 999))
        defaults["allowed_sources"] = _normalize_sources(defaults.get("allowed_sources"))
        defaults["auto_mark"] = bool(defaults.get("auto_mark", True))
        defaults["announce"] = bool(defaults.get("announce", True))
        cfg["defaults"] = defaults

        normalized = {}
        raw_types = cfg.get("seal_types") or {}
        for key, raw in raw_types.items():
            if not isinstance(raw, dict):
                continue
            row = _merge_defaults(defaults, raw)
            row["key"] = str(raw.get("key") or key).strip().lower()
            row["item_short_name"] = str(row.get("item_short_name") or "").strip().lower()
            row["display_name"] = str(row.get("display_name") or row["key"]).strip()
            row["drop_chance"] = max(0.0, min(1.0, float(row.get("drop_chance", defaults["drop_chance"]) or defaults["drop_chance"])))
            row["quantity"] = max(1, int(row.get("quantity", defaults["quantity"]) or defaults["quantity"]))
            row["stack_cap"] = max(1, int(row.get("stack_cap", defaults["stack_cap"]) or defaults["stack_cap"]))
            row["allowed_sources"] = _normalize_sources(row.get("allowed_sources"))
            row["auto_mark"] = bool(row.get("auto_mark", defaults["auto_mark"]))
            row["announce"] = bool(row.get("announce", defaults["announce"]))
            row["message"] = str(row.get("message") or "").rstrip()
            if row["item_short_name"]:
                normalized[row["key"]] = row

        cfg["seal_types"] = normalized
        log.info("seals_loader: loaded %d seal type(s) from Lua", len(normalized))
        return cfg
    except Exception as e:
        log.warning("seals_loader: failed to load Lua config (%s) - using defaults", e)
        return _merge_defaults(_DEFAULTS, {})
