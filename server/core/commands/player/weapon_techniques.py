"""
weapon_techniques.py
--------------------
Player-facing WEAPON verb handler.

Syntax:
  WEAPON LIST [category|type]
  WEAPON HELP <mnemonic>
  WEAPON INFO <mnemonic>
  WEAPON <mnemonic> <target> [<limb>]

Routed here from command_router.py via cmd_weapon().
All actual technique logic lives in Lua (scripts/weapon_techniques/).
This module handles:
  - Input parsing
  - Pre-flight checks that don't need Lua (RT, dead, no session, etc.)
  - Delegating to weapon_api.execute_technique()
  - Auto-grant on training (check_technique_grants, called from training.py)
"""

import logging
from server.core.protocol.colors import colorize, TextPresets, roundtime_msg
from server.core.scripting.lua_bindings.weapon_api import (
    execute_technique,
    check_and_grant_techniques,
    load_techniques_for_session,
)

log = logging.getLogger(__name__)


# ── Mnemonic aliases: players can type partial or alternate spellings ─────────
_ALIASES = {
    # Twin Hammerfists
    "twinhammer":    "twinhammer",
    "twin":          "twinhammer",
    "hammerfist":    "twinhammer",
    "hammerfists":   "twinhammer",
    # Fury
    "fury":          "fury",
    # Clash
    "clash":         "clash",
    # Spin Kick
    "spinkick":      "spinkick",
    "spin":          "spinkick",
    "kick":          "spinkick",
    # Dizzying Swing
    "dizzyingswing": "dizzyingswing",
    "dizzying":      "dizzyingswing",
    "dizzy":         "dizzyingswing",
    # Clobber
    "clobber":       "clobber",
    # Pummel
    "pummel":        "pummel",
    # Pulverize
    "pulverize":     "pulverize",
    # Cripple
    "cripple":       "cripple",
    # Riposte
    "riposte":       "riposte",
    # Flurry
    "flurry":        "flurry",
    # Whirling Blade
    "wblade":        "wblade",
    "whirlingblade": "wblade",
    "whirling":      "wblade",
    # Charge
    "charge":        "charge",
    # Guardant Thrusts
    "gthrusts":      "gthrusts",
    "guardant":      "gthrusts",
    "guardantthrusts": "gthrusts",
    # Cyclone
    "cyclone":       "cyclone",
    # Radial Sweep
    "radialsweep":   "radialsweep",
    "radial":        "radialsweep",
    # Reactive Shot
    "reactiveshot":  "reactiveshot",
    "reactive":      "reactiveshot",
    # Pin Down
    "pindown":       "pindown",
    "pin":           "pindown",
    # Barrage
    "barrage":       "barrage",
    # Volley
    "volley":        "volley",
    # Overpower
    "overpower":     "overpower",
    # Thrash
    "thrash":        "thrash",
    # Reverse Strike
    "reversestrike": "reversestrike",
    "reverse":       "reversestrike",
    # Whirlwind
    "whirlwind":     "whirlwind",
}

# Techniques whose target is the whole room (AoE) — target arg is optional
_AOE_MNEMONICS = {
    "clash", "pulverize", "wblade", "cyclone", "radialsweep",
    "pindown", "volley", "whirlwind",
}

# Valid limb targets for cripple
_VALID_LIMBS = {
    "right arm":  "right arm",
    "left arm":   "left arm",
    "right leg":  "right leg",
    "left leg":   "left leg",
    "right hand": "right hand",
    "left hand":  "left hand",
    "rarm":       "right arm",
    "larm":       "left arm",
    "rleg":       "right leg",
    "lleg":       "left leg",
    "rhand":      "right hand",
    "lhand":      "left hand",
    "arm":        "right arm",
    "leg":        "right leg",
}


def _normalize_limb(raw: str) -> str:
    raw = raw.lower().strip()
    return _VALID_LIMBS.get(raw, raw) if raw in _VALID_LIMBS else raw


def _parse_weapon_args(args: str):
    """
    Parse WEAPON <args> into (subcmd, target_name, limb, filter_word).

    Examples:
      "list"                       -> ("list", "", "", "")
      "list edged"                 -> ("list", "", "", "edged")
      "help cripple"               -> ("help", "", "", "cripple")
      "cripple kobold"             -> ("cripple", "kobold", "", "")
      "cripple kobold right leg"   -> ("cripple", "kobold", "right leg", "")
      "flurry kobold"              -> ("flurry", "kobold", "", "")
      "whirlwind"                  -> ("whirlwind", "", "", "")
    """
    args = (args or "").strip()
    if not args:
        return ("", "", "", "")

    parts = args.split()
    subcmd = parts[0].lower()

    # Meta commands
    if subcmd in ("list",):
        filter_word = parts[1].lower() if len(parts) > 1 else ""
        return ("list", "", "", filter_word)

    if subcmd in ("help", "info"):
        mnemonic = _ALIASES.get(parts[1].lower(), parts[1].lower()) if len(parts) > 1 else ""
        return (subcmd, "", "", mnemonic)

    # Resolve mnemonic alias
    mnemonic = _ALIASES.get(subcmd, subcmd)

    if len(parts) == 1:
        # No target — ok for AoE
        return (mnemonic, "", "", "")

    # parts[1] onward = target + optional limb
    # Limb for cripple: "cripple kobold right leg"
    #                    parts[0]=cripple, parts[1]=kobold, parts[2:]=right leg
    if mnemonic == "cripple" and len(parts) >= 3:
        target_name = parts[1]
        limb_raw    = " ".join(parts[2:])
        limb        = _normalize_limb(limb_raw)
        return (mnemonic, target_name, limb, "")

    target_name = parts[1]
    return (mnemonic, target_name, "", "")


async def cmd_weapon(session, cmd: str, args: str, server):
    """
    Entry point: WEAPON verb.
    """
    if not session or not getattr(session, 'authenticated', False):
        return

    # ── Dead / unconscious checks ─────────────────────────────────────────────
    if getattr(session, 'is_dead', False):
        await session.send_line("You are dead and cannot use weapon techniques.")
        return

    if getattr(session, 'is_unconscious', False):
        await session.send_line("You are unconscious.")
        return

    # ── Roundtime check (reactions are exempt) ────────────────────────────────
    import time as _time
    rt_expires = getattr(session, 'roundtime_expires', 0) or 0
    now        = _time.time()
    if rt_expires > now:
        remaining = rt_expires - now
        # Parse to see if it's a reaction (reactions work during self-inflicted RT)
        subcmd_peek = (args or "").strip().split()[0].lower() if args else ""
        mnemonic_peek = _ALIASES.get(subcmd_peek, subcmd_peek)
        _REACTION_MNEMONICS = {
            "spinkick", "clobber", "riposte", "radialsweep",
            "reactiveshot", "overpower", "reversestrike",
        }
        is_reaction = mnemonic_peek in _REACTION_MNEMONICS
        if not is_reaction:
            await session.send_line(
                colorize(roundtime_msg(remaining), TextPresets.SYSTEM)
            )
            return

    # ── Parse args ────────────────────────────────────────────────────────────
    subcmd, target_name, limb, filter_word = _parse_weapon_args(args)

    if not subcmd:
        await session.send_line(
            "Usage: WEAPON LIST [category]  |  WEAPON HELP <technique>  |  WEAPON <technique> <target>"
        )
        return

    # ── Meta commands (list / help / info) handled fully in Lua ──────────────
    if subcmd in ("list", "help", "info"):
        lua = getattr(server, 'lua', None)
        if not lua or not lua.engine:
            await session.send_line("Weapon technique system unavailable.")
            return
        try:
            engine_table = lua.engine.require("weapon_techniques/engine")
            player_snap  = _build_minimal_player_snap(session, server)
            lua_player   = lua.engine.python_to_lua(player_snap)
            lua_args     = lua.engine.python_to_lua({
                'subcmd': subcmd,
                'arg':    filter_word,
                'target': '',
            })
            raw    = lua.engine.call_hook(engine_table, 'onWeaponVerb', lua_player, lua_args)
            result = lua.engine.lua_to_python(raw) if raw else None
        except Exception as e:
            log.error("WEAPON LIST/HELP Lua error: %s", e)
            result = None

        if result and isinstance(result, dict):
            await session.send_line(result.get('message', ''))
        else:
            await session.send_line("Unable to retrieve weapon technique information.")
        return

    # ── AoE check: these don't require a named target ────────────────────────
    if subcmd in _AOE_MNEMONICS:
        if not target_name:
            target_name = "__room__"

    # ── Non-AoE: require a target ─────────────────────────────────────────────
    elif not target_name:
        await session.send_line(f"Use: WEAPON {subcmd} <target>")
        return

    # ── Execute ───────────────────────────────────────────────────────────────
    message = await execute_technique(session, subcmd, target_name, server, limb=limb)
    if message:
        await session.send_line(message)


def _build_minimal_player_snap(session, server) -> dict:
    """Build a minimal player snapshot for list/help queries (no need for full combat data)."""
    from server.core.scripting.lua_bindings.weapon_api import _session_to_entity
    snap = _session_to_entity(session)
    snap['weapon_techniques'] = getattr(session, 'weapon_techniques', {}) or {}
    return snap


# ── Auto-grant hook — called from training.py ─────────────────────────────────

async def check_technique_grants(session, skill_id: int, new_ranks: int, server):
    """
    Called by training.py after a weapon skill rank increase.
    Checks for newly available techniques and grants them.
    Sends grant messages to the player.

    skill_id maps to skill name per SKILL_NAMES in training.py:
        5  = edged_weapons
        6  = blunt_weapons
        7  = two_handed_weapons
        8  = ranged_weapons
        10 = polearm_weapons
        11 = brawling
    """
    _WEAPON_SKILL_MAP = {
        5:  "edged_weapons",
        6:  "blunt_weapons",
        7:  "two_handed_weapons",
        8:  "ranged_weapons",
        10: "polearm_weapons",
        11: "brawling",
    }
    skill_name = _WEAPON_SKILL_MAP.get(skill_id)
    if not skill_name:
        return  # Not a weapon skill — nothing to grant

    messages = await check_and_grant_techniques(session, skill_name, new_ranks, server)
    for msg in messages:
        await session.send_line(msg)
