"""
sync_broadcaster.py
-------------------
Builds JSON state snapshots from live session objects and feeds them
to SyncServer for delivery to connected clients.

Called from the game loop every 10 ticks (~1 second).

Snapshot schema (sent as a single JSON line + newline):
{
  "type": "state",
  "ts":   1234567890.123,          # server unix timestamp
  "character": {
    "name": "Laernu",
    "level": 12,
    "profession": "Rogue",
    "race": "Human"
  },
  "vitals": {
    "hp": 85,  "hp_max": 120,
    "mp": 45,  "mp_max": 100,
    "sp": 30,  "sp_max": 89,
    "stamina": 79, "stamina_max": 89
  },
  "xp": {
    "total": 12500,
    "field": 800,
    "level": 12,
    "tnl": 3200,
    "mind_state": "contemplating",
    "mind_idx": 4,
    "absorption_pct": 45
  },
  "status_effects": [
    {
      "id": "bleeding",
      "name": "Bleeding",
      "category": "DEBUFF_DOT",
      "stacks": 2,
      "remaining": 45.2,       # seconds remaining; -1 = indefinite
      "prompt_char": "!"
    }
  ],
  "combat": {
    "in_combat": true,
    "target": "lesser ghoul",
    "target_hp_pct": 0.42      # 0.0-1.0; null if no target
  },
  "position": "standing",
  "encumbrance": {
    "tier": 0,
    "name": "None",
    "carried_lbs": 18.5,
    "cap_lbs": 80.0,
    "pct": 23
  },
  "silver": 1250,
  "prompt": "[!]"
}
"""

import time
import json
import logging
from decimal import Decimal

log = logging.getLogger(__name__)

# GS4 mind state list — must match experience_manager.MIND_STATES thresholds.
# Ordered from empty (0) to full (8).  Used for mind_idx in the xp snapshot.
MIND_STATES = [
    "clear as a bell",    # 0%  fill
    "clear",              # 12%
    "fresh and clear",    # 25%
    "fresh",              # 40%
    "muddled",            # 55%
    "becoming saturated", # 70%
    "saturated",          # 85%
    "you must rest!",     # 95%
    "fried",              # 100%
]


def _json_safe(value):
    """Recursively normalize common non-JSON-native values for sync snapshots."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return value


def build_snapshot(session, server) -> dict:
    """
    Build a complete state snapshot dict from a live session.
    Safe to call every second — all reads are simple attribute lookups.
    """
    # ── Vitals ──────────────────────────────────────────────────────────────
    vitals = {
        "hp":          int(getattr(session, "health_current",  0)),
        "hp_max":      int(getattr(session, "health_max",      100)),
        "mp":          int(getattr(session, "mana_current",    0)),
        "mp_max":      int(getattr(session, "mana_max",        0)),
        "sp":          int(getattr(session, "spirit_current",  0)),
        "sp_max":      int(getattr(session, "spirit_max",      10)),
        "stamina":     int(getattr(session, "stamina_current", 0)),
        "stamina_max": int(getattr(session, "stamina_max",     100)),
    }

    # ── XP ──────────────────────────────────────────────────────────────────
    # session.mind_state is NOT a stored attribute — it is always computed on
    # the fly from field_experience by experience_manager.get_mind_state().
    # Reading it as a raw attribute always returns the default ("clear").
    field_xp = int(getattr(session, "field_experience", 0))
    total_xp = int(getattr(session, "experience",       0))
    level    = int(getattr(session, "level",            1))
    tnl      = int(getattr(session, "experience_tnl",   0))

    try:
        from server.core.engine.experience.experience_manager import (
            get_mind_state   as _get_mind_state,
            get_mind_fill_pct as _get_mind_fill_pct,
        )
        mind_raw = _get_mind_state(session).lower().strip()
        absorb   = int(_get_mind_fill_pct(session) * 100)
    except Exception:
        mind_raw = "clear"
        absorb   = 0

    # Resolve mind_idx: scan MIND_STATES for the best substring match
    # (e.g. "becoming saturated" matches "becoming saturated" at index 5)
    mind_idx = 0
    for i, label in enumerate(MIND_STATES):
        if label in mind_raw or mind_raw in label:
            mind_idx = i
            break

    xp = {
        "total":          total_xp,
        "field":          field_xp,
        "level":          level,
        "tnl":            tnl,
        "mind_state":     mind_raw,
        "mind_idx":       mind_idx,
        "absorption_pct": absorb,
    }

    # ── Status effects ───────────────────────────────────────────────────────
    status_effects = []
    sm = getattr(server, "status", None)
    if sm:
        for se in sm.get_all_active(session):
            defn = sm.get_def(se.effect_id) or {}
            status_effects.append({
                "id":          se.effect_id,
                "name":        defn.get("name", se.effect_id),
                "category":    defn.get("category", ""),
                "stacks":      se.stacks,
                "remaining":   round(se.remaining, 1),
                "prompt_char": defn.get("prompt_char"),
            })
    else:
        # Fallback: read raw dict format from old status_effects system
        raw = getattr(session, "status_effects", {}) or {}
        for eid, data in raw.items():
            if isinstance(data, dict):
                exp = data.get("expires", 0)
                rem = max(0.0, exp - time.time()) if exp > 0 else -1
                status_effects.append({
                    "id":          eid,
                    "name":        eid.replace("_", " ").title(),
                    "category":    "",
                    "stacks":      data.get("stacks", 1),
                    "remaining":   round(rem, 1),
                    "prompt_char": None,
                })

    # ── Position-based status synthesis & cleanup ───────────────────────────
    # Source of truth is ALWAYS session.position, not StatusManager.
    # This prevents stale indefinite effects from lingering after STAND.
    pos = getattr(session, "position", "standing")

    # Position effects that must be removed when standing
    POSITION_EFFECT_IDS = {"sleeping", "sitting", "kneeling", "resting", "prone"}

    if pos == "standing":
        # Strip any position-based effects that StatusManager still holds —
        # they linger because duration=-1 and only explicit remove clears them.
        # The icon bar must reflect reality: player is standing = no position fx.
        status_effects = [e for e in status_effects
                          if e.get("id") not in POSITION_EFFECT_IDS]
    else:
        # Synthesize the correct position effect if StatusManager missed it
        active_ids = {e["id"] for e in status_effects}
        pos_map = {
            "sleeping": ("sleeping", "Sleeping",  "STATE",       -1, None),
            "sitting":  ("sitting",  "Sitting",   "STATE",       -1, "s"),
            "kneeling": ("kneeling", "Kneeling",  "STATE",       -1, "K"),
            "lying":    ("prone",    "Prone",      "DEBUFF_STAT", -1, "p"),
        }
        if pos in pos_map:
            eid, name, cat, rem, pchar = pos_map[pos]
            if eid not in active_ids:
                status_effects.append({
                    "id":          eid,
                    "name":        name,
                    "category":    cat,
                    "stacks":      1,
                    "remaining":   rem,
                    "prompt_char": pchar,
                })

    # Also synthesize in_combat from raw boolean if StatusManager missed it
    active_ids = {e["id"] for e in status_effects}
    if "in_combat" not in active_ids and getattr(session, "in_combat", False):
        status_effects.append({
            "id":          "in_combat",
            "name":        "In Combat",
            "category":    "STATE",
            "stacks":      1,
            "remaining":   -1,
            "prompt_char": None,
        })

    # ── Combat ───────────────────────────────────────────────────────────────
    in_combat   = bool(getattr(session, "in_combat", False))
    target      = getattr(session, "target", None)
    target_name = None
    target_hp   = None
    if target and getattr(target, "alive", False):
        target_name = getattr(target, "full_name", None) or getattr(target, "name", None)
        t_cur = getattr(target, "health_current", 0)
        t_max = getattr(target, "health_max", 1)
        target_hp = round(t_cur / max(1, t_max), 3)

    combat = {
        "in_combat":     in_combat,
        "target":        target_name,
        "target_hp_pct": target_hp,
    }

    # ── Encumbrance ─────────────────────────────────────────────────────────
    encumbrance = _build_encumbrance(session, server)

    # ── Prompt string ────────────────────────────────────────────────────────
    prompt = sm.get_prompt_string(session) if sm else ""

    # ── Character info ───────────────────────────────────────────────────────
    character = {
        "name":       getattr(session, "character_name", ""),
        "level":      level,
        "profession": getattr(session, "profession", ""),
        "race":       getattr(session, "race",       ""),
    }

    # ── Stance ───────────────────────────────────────────────────────────────
    stance = getattr(session, "stance", "offensive") or "offensive"

    # ── Training points ───────────────────────────────────────────────────────
    ptp = int(getattr(session, "physical_tp", 0) or 0)
    mtp = int(getattr(session, "mental_tp",   0) or 0)

    # ── TNL (experience to next level) ────────────────────────────────────────
    tnl = 0
    try:
        exp_mgr = getattr(server, "experience", None)
        if exp_mgr:
            next_xp = exp_mgr.xp_for_level(level + 1)
            tnl = max(0, next_xp - int(getattr(session, "experience", 0)))
    except Exception:
        tnl = xp.get("tnl", 0)

    # Update xp dict with authoritative TNL
    xp["tnl"] = tnl

    # ── Time & Weather ────────────────────────────────────────────────────────
    time_weather = {}
    try:
        from server.core.engine.time.elanthian_clock import ElanthianClock
        snap_t = ElanthianClock.now()
        time_weather["day_name"]       = snap_t["day_name"]
        time_weather["month_name"]     = snap_t["month_name"]
        time_weather["day"]            = snap_t["day"]
        time_weather["elanthian_year"] = snap_t["elanthian_year"]
        time_weather["period"]         = snap_t["period"]
        time_weather["hour_name"]      = snap_t["hour_name"]
        time_weather["time_24"]        = snap_t["time_24"]
        time_weather["holiday"]        = snap_t.get("holiday")
    except Exception:
        pass

    try:
        weather_mgr = getattr(server, "weather", None)
        room        = getattr(session, "current_room", None)
        if weather_mgr and room:
            w = weather_mgr.get_room_weather(room)
            time_weather["weather_state"]   = w.get("state", "clear")
            time_weather["weather_label"]   = weather_mgr.get_weather_label(
                getattr(room, "zone_id", 0)
            )
            time_weather["weather_forced"]  = w.get("forced_by") is not None
            time_weather["precipitation"]   = weather_mgr.is_precipitation(
                getattr(room, "zone_id", 0)
            )
            time_weather["indoor"]          = getattr(room, "indoor", False)
    except Exception:
        pass

    room = getattr(session, "current_room", None)

    return {
        "type":           "state",
        "ts":             time.time(),
        "character":      character,
        "room":           {
            "id": getattr(room, "id", None),
            "title": getattr(room, "title", ""),
            "zone_name": getattr(room, "zone_name", ""),
        } if room else None,
        "vitals":         vitals,
        "xp":             xp,
        "status_effects": status_effects,
        "combat":         combat,
        "position":       getattr(session, "position", "standing"),
        "encumbrance":    encumbrance,
        "silver":         int(getattr(session, "silver", 0)),
        "prompt":         prompt,
        "stance":         stance,
        "ptp":            ptp,
        "mtp":            mtp,
        "time_weather":   time_weather,
        "room_enemies":   _build_room_enemies(session, server),
        "room_npcs":      _build_room_npcs(session, server),
        "wounds":         _build_wounds(session),
        "right_hand":     _item_noun(getattr(session, "right_hand", None)),
        "left_hand":      _item_noun(getattr(session, "left_hand",  None)),
    }


def _item_noun(item: dict) -> str | None:
    """Return a short identifier for a held item, or None if hand is empty."""
    if not item:
        return None
    return item.get("noun") or item.get("short_name") or item.get("name") or "item"


def _build_room_enemies(session, server) -> list[dict]:
    """Build a duplicate-safe list of room creatures for the target button."""
    room = getattr(session, "current_room", None)
    creature_mgr = getattr(server, "creatures", None)
    if not room or not creature_mgr:
        return []

    counts = {}
    out = []
    creatures = creature_mgr.get_creatures_in_room(room.id)
    creatures = sorted(
        creatures,
        key=lambda c: (str(getattr(c, "name", "")).lower(), int(getattr(c, "id", 0))),
    )

    for creature in creatures:
        if not getattr(creature, "alive", True):
            continue
        name = str(getattr(creature, "name", "") or "").strip()
        if not name:
            continue

        match = name.lower()
        counts[match] = counts.get(match, 0) + 1
        ordinal = counts[match]
        token = name if ordinal == 1 else f"{ordinal} {name}"
        out.append({
            "token": token,
            "display": token,
            "match": match,
        })

    return out


def _build_room_npcs(session, server) -> list[dict]:
    """Build clickable NPC interaction data for the current room."""
    room = getattr(session, "current_room", None)
    npc_mgr = getattr(server, "npcs", None)
    if not room or not npc_mgr:
        return []

    out = []
    for npc in npc_mgr.get_npcs_in_room(room.id):
        try:
            actions = _build_npc_actions(session, server, npc)
        except Exception:
            log.exception("Failed building NPC actions for %s", getattr(npc, "template_id", "unknown"))
            actions = []

        if not actions:
            continue

        aliases = []
        for value in (
            getattr(npc, "name", None),
            getattr(npc, "display_name", None),
            getattr(npc, "full_name", None),
        ):
            text = str(value or "").strip()
            if text and text not in aliases:
                aliases.append(text)

        if not aliases:
            continue

        out.append({
            "template_id": getattr(npc, "template_id", ""),
            "name": getattr(npc, "name", ""),
            "display": getattr(npc, "display_name", getattr(npc, "name", "")),
            "aliases": aliases,
            "marker": " ·",
            "actions": actions,
        })

    return out


def _build_npc_actions(session, server, npc) -> list[dict]:
    """Return context-sensitive actions that are valid/useful for this player."""
    actions = []
    seen: set[tuple[str, str, bool]] = set()
    npc_target = str(getattr(npc, "name", "") or getattr(npc, "display_name", "") or "").strip()
    if not npc_target:
        return actions

    def add(label: str, command: str, *, prefill: bool = False):
        key = (label, command, prefill)
        if not command or key in seen:
            return
        seen.add(key)
        actions.append({
            "label": label,
            "command": command,
            "prefill": bool(prefill),
        })

    service_tags = []
    try:
        service_tags = sorted(getattr(npc, "get_service_tags", lambda: set())() or [])
    except Exception:
        service_tags = []

    dialogue_map = getattr(npc, "dialogues", {}) or {}
    rich_topics = [key for key in dialogue_map.keys() if str(key or "").strip() and str(key).strip() != "default"]
    has_social = bool(
        rich_topics
        or getattr(npc, "greeting", None)
        or service_tags
        or getattr(npc, "guild_id", None)
        or (getattr(npc, "can_shop", False) and getattr(npc, "shop_id", None))
    )
    if has_social:
        add("Talk", f"talk to {npc_target}")

    dialogue_keys = list((getattr(npc, "dialogues", {}) or {}).keys())
    for topic in dialogue_keys[:8]:
        topic = str(topic or "").strip()
        if not topic or topic == "default":
            continue
        add(f"Ask about {topic}", f"ask {npc_target} about {topic}")

    if getattr(npc, "can_shop", False) and getattr(npc, "shop_id", None):
        add("Order", "order")
        add("Buy...", "buy ", prefill=True)
        add("Sell...", "sell ", prefill=True)
        add("Appraise...", "appraise ", prefill=True)

    if "bank" in service_tags:
        add("Check balance", "check balance")
        add("Deposit...", "deposit ", prefill=True)
        add("Withdraw...", "withdraw ", prefill=True)
        add("Locker info", "locker info")
    if "healer" in service_tags:
        add("Ask about healing", f"ask {npc_target} about healing")
    if "travel" in service_tags:
        add("Ask about travel", f"ask {npc_target} about travel")
    if "registrar" in service_tags:
        add("Ask about registration", f"ask {npc_target} about registration")
    if "inn" in service_tags:
        add("Ask about rooms", f"ask {npc_target} about room")
    if "pawnbroker" in service_tags:
        add("Order", "order")
        add("Sell...", "sell ", prefill=True)
        add("Appraise...", "appraise ", prefill=True)
        add("Backroom", "backroom")
        add("Weapon table", "look on weapon table")
        add("Armor table", "look on armor table")
        add("Arcana table", "look on arcana table")
        add("Misc table", "look on misc table")
        add("Buy backroom...", "buy backroom ", prefill=True)
    if "priest" in service_tags:
        add("Ask about arkati", f"ask {npc_target} about arkati")
    if "locksmith" in service_tags:
        add("Order", "order")
        add("Ring bell", "ring bell")
        add("My jobs", "myjobs")
        add("Pay...", "pay ", prefill=True)

    _extend_guild_actions(actions, seen, session, server, npc)
    _extend_quest_actions(actions, seen, session, server, npc)
    return actions


def _extend_guild_actions(actions: list[dict], seen: set[tuple[str, str, bool]], session, server, npc) -> None:
    guild_id = getattr(npc, "guild_id", None)
    db = getattr(server, "db", None)
    if not guild_id or not db:
        return

    guild_def = db.get_guild_definition(guild_id)
    if not guild_def:
        return

    def add(label: str, command: str, *, prefill: bool = False):
        key = (label, command, prefill)
        if not command or key in seen:
            return
        seen.add(key)
        actions.append({
            "label": label,
            "command": command,
            "prefill": bool(prefill),
        })

    membership = getattr(session, "guild_membership", None)
    same_guild = bool(membership and membership.get("guild_id") == guild_id)
    profession_ok = int(guild_def.get("profession_id") or 0) == int(getattr(session, "profession_id", 0) or 0)
    join_level = int(guild_def.get("join_level") or 15)

    if not profession_ok:
        add("Ask about guild", f"ask {getattr(npc, 'name', 'npc')} about guild")
        return

    if not same_guild:
        if int(getattr(session, "level", 0) or 0) >= join_level:
            add("Join guild", "gld join")
        add("Ask about guild", f"ask {getattr(npc, 'name', 'npc')} about guild")
        add("Ask about joining", f"ask {getattr(npc, 'name', 'npc')} about join")
        return

    add("Guild status", "gld status")
    add("Guild rank", "gld rank")
    add("Guild skills", "gld skills")
    add("Guild check-in", "gld checkin")

    if int(guild_def.get("monthly_dues") or 0) > 0 and not int(membership.get("is_guildmaster", 0) or 0):
        add("Pay dues...", "gld pay ", prefill=True)

    if int(guild_def.get("has_skill_training") or 0):
        add("Get guild task", "gld task")
        add("Practice", "gld practice")
        add("Complete task", "gld complete")
        add("Swap task...", "gld swap ", prefill=True)
        add("Vouchers", "gld vouchers")

    if guild_id == "rogue":
        add("Start guild quest", "gld quest start")
        add("Guild quest status", "gld quest")
        add("Guild password", "gld password")

    if int(membership.get("is_guildmaster", 0) or 0):
        add("Invite...", "gld invite ", prefill=True)
        add("Initiate...", "gld initiate ", prefill=True)
        add("Nominate...", "gld nominate ", prefill=True)
        add("Promote...", "gld promote ", prefill=True)

    add("Resign guild", "gld resign")


def _extend_quest_actions(actions: list[dict], seen: set[tuple[str, str, bool]], session, server, npc) -> None:
    quest_engine = getattr(server, "guild", None)
    if not quest_engine or not getattr(session, "character_id", None):
        return

    def add(label: str, command: str, *, prefill: bool = False):
        key = (label, command, prefill)
        if not command or key in seen:
            return
        seen.add(key)
        actions.append({
            "label": label,
            "command": command,
            "prefill": bool(prefill),
        })

    offers = quest_engine.get_npc_startable_quests(session, npc)
    related = quest_engine.get_npc_related_active_quests(session, npc)

    npc_name = getattr(npc, "name", "npc")
    guild_engine = getattr(server, "guild", None)
    authority = getattr(guild_engine, "_get_adventurer_authority", lambda _npc: None)(npc) if guild_engine else None
    if authority:
        add("Status", "bounty status")
        add("Register", f"ask {npc_name} about register")
        add("Bounty", f"ask {npc_name} about bounty")
        add("Rank", f"ask {npc_name} about rank")
        add("Check-in", f"ask {npc_name} about checkin")
        add("Vouchers", f"ask {npc_name} about vouchers")
        add("Easier", f"ask {npc_name} about easier")
        add("Harder", f"ask {npc_name} about harder")
        add("Remove", f"ask {npc_name} about remove")
        add("Swap", f"ask {npc_name} about swap")
        add("Share...", "bounty add ", prefill=True)

    if not offers and not related:
        return

    add("Ask about work", f"ask {npc_name} about work")
    add("Quest status", "quest")

    if any(row.get("hint") for row in related):
        add("Quest hint", "quest hint")

    for row in related:
        stage = row.get("current_stage") or {}
        if stage.get("quiz_questions"):
            add("Answer...", "answer ", prefill=True)
            break

    for row in offers[:4]:
        title = str(row.get("title", "Quest")).strip() or "Quest"
        if len(title) > 24:
            title = title[:21] + "..."
        add(f"Start {title}", f"quest start {row.get('key_name')}")



def _build_wounds(session) -> dict:
    """Serialize session.wounds (WoundBridge) for the sync snapshot.
    Falls back to session.injuries if wounds not populated (legacy compat).
    """
    # Primary: WoundBridge-managed session.wounds dict
    wounds_dict = getattr(session, "wounds", None)
    if wounds_dict:
        out = {}
        for loc_key, entry in wounds_dict.items():
            if not isinstance(entry, dict):
                continue
            wr = int(entry.get("wound_rank", 0))
            sr = int(entry.get("scar_rank", 0))
            if wr <= 0 and sr <= 0:
                continue
            out[loc_key] = {
                "wound_rank":  wr,
                "scar_rank":   sr,
                "is_bleeding": bool(entry.get("is_bleeding", False)),
                "bandaged":    bool(entry.get("bandaged", False)),
            }
        return out

    # Fallback: legacy session.injuries {location: severity_int}
    injuries = getattr(session, "injuries", None) or {}
    is_bleeding = False
    raw_fx = getattr(session, "status_effects", {}) or {}
    if isinstance(raw_fx, dict):
        is_bleeding = "bleeding" in raw_fx or "major_bleed" in raw_fx
    else:
        try:
            is_bleeding = any(
                getattr(se, "effect_id", "") in ("bleeding", "major_bleed")
                for se in raw_fx
            )
        except Exception:
            pass
    out = {}
    for loc, severity in injuries.items():
        sev = int(severity or 0)
        if sev <= 0:
            continue
        loc_key = loc.strip().lower().replace(" ", "_")
        out[loc_key] = {
            "wound_rank":  sev,
            "scar_rank":   0,
            "is_bleeding": is_bleeding,
            "bandaged":    False,
        }
    return out


def _build_encumbrance(session, server) -> dict:
    """Build encumbrance summary, using the encumbrance module if available."""
    try:
        from server.core.engine.encumbrance import (
            carry_capacity, carried_weight, encumbrance_pct,
            encumbrance_tier, encumbrance_name, TIER_NAMES
        )
        carried = carried_weight(session)
        cap     = carry_capacity(session)
        pct     = encumbrance_pct(session)
        tier    = encumbrance_tier(session)
        name    = encumbrance_name(session)
        return {
            "tier":        tier,
            "name":        name,
            "carried_lbs": round(carried, 1),
            "cap_lbs":     round(cap, 1),
            "pct":         int(pct),
        }
    except Exception:
        return {"tier": 0, "name": "None", "carried_lbs": 0, "cap_lbs": 80, "pct": 0}


class SyncBroadcaster:
    """
    Schedules state pushes to all connected sync clients.
    Called from the game loop every 10 ticks (1 second).
    """

    def __init__(self, server):
        self._server = server

    async def broadcast_all(self):
        """Push a fresh snapshot to every connected sync client."""
        sync_srv = getattr(self._server, "sync_server", None)
        if not sync_srv or not sync_srv.has_connections():
            return

        sessions = list(self._server.world.get_all_players())
        for session in sessions:
            if session.state != "playing" or not session.character_id:
                continue
            if not sync_srv.is_connected(session.character_id):
                continue
            try:
                snapshot = _json_safe(build_snapshot(session, self._server))
                line     = json.dumps(snapshot, separators=(",", ":")) + "\n"
                await sync_srv.send(session.character_id, line)
            except Exception as e:
                log.exception("SyncBroadcaster: error pushing to %s: %s",
                              session.character_name, e)
