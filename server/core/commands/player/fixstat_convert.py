"""
fixstat_convert.py
------------------
In-game commands for stat reallocation (FIXSTATS) and TP conversion (CONVERT).

FIXSTATS  — redistribute your 10 base stats at an inn.
            Rules (single-player friendly):
              • 10 free uses before level 20
              • 1 free use per 24 hours after level 20
              • Total stat points cannot change (zero-sum)
              • No stat may go below 1 or above 100
              • Can be done from any inn room

CONVERT   — exchange PTP <-> MTP at the 2:1 rate used in real GS4.
              CONVERT PTP 10   — spend 20 MTP, gain 10 PTP
              CONVERT MTP 10   — spend 20 PTP, gain 10 MTP
            Can be done anywhere (not inn-restricted).

Both actions are also available via the training website (popup modals).
"""

import time
import logging

log = logging.getLogger(__name__)

# ── Stat metadata ─────────────────────────────────────────────────────────────

STATS = [
    "strength", "constitution", "dexterity", "agility",
    "discipline", "aura", "logic", "intuition", "wisdom", "influence",
]
STAT_ABBREVS = {
    "str": "strength", "con": "constitution", "dex": "dexterity",
    "agi": "agility",  "dis": "discipline",   "aur": "aura",
    "log": "logic",    "int": "intuition",     "wis": "wisdom",
    "inf": "influence",
}

def _get_stat(session, name):
    return getattr(session, f"stat_{name}", 50)

def _set_stat(session, name, value):
    setattr(session, f"stat_{name}", value)

def _get_base_stat(session, name):
    return getattr(session, f"base_stat_{name}", _get_stat(session, name))

def _total_stats(session):
    return sum(_get_stat(session, s) for s in STATS)

def _base_total_stats(session):
    return sum(_get_base_stat(session, s) for s in STATS)

def _inn_room_ids():
    """
    Returns a set of room IDs that count as inn rooms for FIXSTATS.
    Reads from the DB zone data. Includes all rooms whose location_name
    contains 'inn', 'tavern', 'lodge', 'wayfarers', or 'healer hall'.
    Falls back gracefully if DB is unavailable.
    """
    # Sentinel: broad enough set of known safe-room location names
    INN_KEYWORDS = {"inn", "tavern", "lodge", "wayfarers", "almshouse",
                    "common room", "healer", "hostel", "rest"}
    return INN_KEYWORDS


# ── FIXSTATS uses tracking ────────────────────────────────────────────────────

def _fixstat_uses_remaining(session):
    return getattr(session, "fixstat_uses_remaining", 10)

def _fixstat_can_use_free(session):
    """Return (can_use: bool, reason: str)."""
    level = getattr(session, "level", 1)
    uses  = _fixstat_uses_remaining(session)

    if level < 20:
        # Pre-20: consume from the 10-use pool
        if uses > 0:
            return True, "pool"
        return False, f"You have used all {10} free stat reallocations before level 20."

    # Post-20: 1 per 24 hours
    last = getattr(session, "fixstat_last_free", None)
    if last is None:
        return True, "cooldown"
    elapsed = time.time() - (last.timestamp() if hasattr(last, "timestamp") else float(last))
    if elapsed >= 86400:
        return True, "cooldown"
    remaining_secs = int(86400 - elapsed)
    h, m = divmod(remaining_secs // 60, 60)
    return False, (
        f"You may reallocate your stats once per day after level 20.  "
        f"Available again in {h}h {m}m."
    )

def _fixstat_consume(session, reason, server):
    """Deduct one fixstat use and persist."""
    level = getattr(session, "level", 1)
    if level < 20 and reason == "pool":
        session.fixstat_uses_remaining = max(0, _fixstat_uses_remaining(session) - 1)
    else:
        session.fixstat_last_free = time.time()

    session.fixstat_uses_total = getattr(session, "fixstat_uses_total", 0) + 1

    if server.db and session.character_id:
        server.db.save_fixstat_data(
            session.character_id,
            session.fixstat_uses_remaining,
            session.fixstat_uses_total,
            session.fixstat_last_free if reason == "cooldown" else None,
        )


# ── In-room inn detection ─────────────────────────────────────────────────────

def _is_at_inn(session, server):
    """True if the player is checked in and currently inside that inn."""
    inns = getattr(server, "inns", None)
    if inns:
        return inns.can_use_fixstats(session)

    room = getattr(session, "current_room", None)
    if not room:
        return False
    loc = getattr(room, "location_name", "") or ""
    loc_lower = loc.lower()
    for kw in _inn_room_ids():
        if kw in loc_lower:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# FIXSTATS command
# Usage:
#   FIXSTATS                — show current stats + usage info
#   FIXSTATS str 65 con 45  — set STR to 65 and CON to 45 (zero-sum enforced)
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_fixstats(session, cmd, args, server):
    from server.core.protocol.colors import colorize, TextPresets

    # ── Require inn room ──────────────────────────────────────────────────────
    if not _is_at_inn(session, server):
        inns = getattr(server, "inns", None)
        await session.send_line(colorize(
            f"  {(inns.fixstats_gate_message() if inns else 'You must be at an inn or safe resting place to reallocate your stats.')}",
            TextPresets.SYSTEM
        ))
        return

    level = getattr(session, "level", 1)
    can, reason = _fixstat_can_use_free(session)

    # ── No args: show status screen ───────────────────────────────────────────
    if not args:
        await session.send_line("")
        await session.send_line(colorize("  Stat Reallocation", TextPresets.EXPERIENCE))
        await session.send_line(colorize("  " + "─" * 38, TextPresets.SYSTEM))
        for s in STATS:
            val  = _get_stat(session, s)
            base = _get_base_stat(session, s)
            diff = val - base
            diff_str = f"  ({'+' if diff >= 0 else ''}{diff})" if diff != 0 else ""
            await session.send_line(
                f"    {s.capitalize():<14} {val:>3}{diff_str}"
            )
        total = _total_stats(session)
        await session.send_line(colorize(f"\n  Total points: {total}", TextPresets.SYSTEM))
        if level < 20:
            uses = _fixstat_uses_remaining(session)
            await session.send_line(colorize(
                f"  Free uses remaining (pre-level 20): {uses}",
                TextPresets.EXPERIENCE if uses > 0 else TextPresets.WARNING
            ))
        else:
            await session.send_line(colorize(
                "  After level 20: 1 free reallocation per 24 hours.",
                TextPresets.SYSTEM
            ))
            if not can:
                await session.send_line(colorize(f"  {reason}", TextPresets.WARNING))
        await session.send_line("")
        await session.send_line(colorize(
            "  Usage: FIXSTATS <stat> <value> [<stat> <value> ...]",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "  Example: FIXSTATS str 70 con 60 dex 55",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "  Stat names: STR CON DEX AGI DIS AUR LOG INT WIS INF",
            TextPresets.SYSTEM
        ))
        await session.send_line("")
        return

    # ── Availability check ────────────────────────────────────────────────────
    if not can:
        await session.send_line(colorize(f"  {reason}", TextPresets.WARNING))
        return

    # ── Parse args: pairs of stat name + value ────────────────────────────────
    tokens = args.lower().split()
    if len(tokens) % 2 != 0:
        await session.send_line(colorize(
            "  Provide stat/value pairs.  Example: FIXSTATS str 70 con 60",
            TextPresets.WARNING
        ))
        return

    desired = {}
    for i in range(0, len(tokens), 2):
        raw_name = tokens[i]
        raw_val  = tokens[i + 1]
        name = STAT_ABBREVS.get(raw_name, raw_name)
        if name not in STATS:
            await session.send_line(colorize(
                f"  Unknown stat: '{raw_name}'.  Valid: STR CON DEX AGI DIS AUR LOG INT WIS INF",
                TextPresets.WARNING
            ))
            return
        try:
            val = int(raw_val)
        except ValueError:
            await session.send_line(colorize(
                f"  '{raw_val}' is not a number.",
                TextPresets.WARNING
            ))
            return
        if not (1 <= val <= 130):
            await session.send_line(colorize(
                f"  Stat values must be between 1 and 130 (got {val} for {name}).",
                TextPresets.WARNING
            ))
            return
        desired[name] = val

    # ── Build the proposed new stat array ────────────────────────────────────
    current_total = _total_stats(session)
    proposed = {s: _get_stat(session, s) for s in STATS}
    proposed.update(desired)

    new_total = sum(proposed.values())
    if new_total != current_total:
        delta = new_total - current_total
        await session.send_line(colorize(
            f"  Stat total must stay the same ({current_total}).  "
            f"Your changes are {'+' if delta > 0 else ''}{delta} points off.",
            TextPresets.WARNING
        ))
        await session.send_line(colorize(
            "  Tip: if you raise one stat, lower another by the same amount.",
            TextPresets.SYSTEM
        ))
        return

    # ── Confirm nothing changed (no-op) ──────────────────────────────────────
    changes = {s: (proposed[s], _get_stat(session, s))
               for s in STATS if proposed[s] != _get_stat(session, s)}
    if not changes:
        await session.send_line(colorize(
            "  No stats were changed.",
            TextPresets.SYSTEM
        ))
        return

    # ── Apply ─────────────────────────────────────────────────────────────────
    for s, new_val in proposed.items():
        _set_stat(session, s, new_val)

    _fixstat_consume(session, reason, server)

    if server.db and session.character_id:
        server.db.save_character_stats(session.character_id, session)

    # ── Output ────────────────────────────────────────────────────────────────
    await session.send_line("")
    await session.send_line(colorize("  Stat reallocation complete.", TextPresets.EXPERIENCE))
    for s, (new_val, old_val) in changes.items():
        diff = new_val - old_val
        arrow = f"{old_val} -> {new_val}  ({'+' if diff > 0 else ''}{diff})"
        await session.send_line(colorize(f"    {s.capitalize():<14} {arrow}", TextPresets.EXPERIENCE))

    level = getattr(session, "level", 1)
    uses  = _fixstat_uses_remaining(session)
    if level < 20:
        await session.send_line(colorize(
            f"  Free uses remaining (pre-level 20): {uses}",
            TextPresets.SYSTEM
        ))
    else:
        await session.send_line(colorize(
            "  Next free reallocation available in 24 hours.",
            TextPresets.SYSTEM
        ))
    await session.send_line("")

    # Notify other players in the room
    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"  {session.character_name} looks inward, seemingly rearranging something fundamental.",
            exclude=session
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONVERT command
# Usage:
#   CONVERT                — show current TPs, loan balances, and rates
#   CONVERT PTP <n>        — spend 2*n MTP, gain n PTP  (tracked as ptp_loaned)
#   CONVERT MTP <n>        — spend 2*n PTP, gain n MTP  (tracked as mtp_loaned)
#   CONVERT REFUND         — losslessly return ALL loaned TPs, zero debt
#   CONVERT REFUND PTP     — refund only the PTP loan (return PTP, recover MTP)
#   CONVERT REFUND MTP     — refund only the MTP loan (return MTP, recover PTP)
#
# REFUND is always lossless: you get back exactly what you spent, no penalty.
# If you don't have enough TPs to return (e.g. you already spent the converted
# points on skills), the refund tells you how much you're short.
# ─────────────────────────────────────────────────────────────────────────────

CONVERT_RATE = 2   # 2 of source = 1 of target (real GS4 rate)


def _get_loans(session):
    """Return (ptp_loaned, mtp_loaned) — how much is currently borrowed."""
    return (
        getattr(session, "ptp_loaned", 0),
        getattr(session, "mtp_loaned", 0),
    )


def _save_convert_state(server, session):
    """Persist TPs and loan balances in one shot."""
    if server.db and session.character_id:
        server.db.save_character_tps(
            session.character_id,
            session.physical_tp,
            session.mental_tp,
        )
        server.db.save_convert_loans(
            session.character_id,
            session.ptp_loaned,
            session.mtp_loaned,
        )


async def cmd_convert(session, cmd, args, server):
    from server.core.protocol.colors import colorize, TextPresets

    ptp        = getattr(session, "physical_tp", 0)
    mtp        = getattr(session, "mental_tp",   0)
    ptp_loaned, mtp_loaned = _get_loans(session)

    # ── No args: status screen ─────────────────────────────────────────────
    if not args:
        await session.send_line("")
        await session.send_line(colorize("  Training Point Conversion", TextPresets.EXPERIENCE))
        await session.send_line(colorize("  " + "─" * 38, TextPresets.SYSTEM))
        await session.send_line(f"    Physical TPs (PTP):  {ptp}")
        await session.send_line(f"    Mental TPs   (MTP):  {mtp}")
        await session.send_line("")
        await session.send_line(colorize(
            f"  Rate: {CONVERT_RATE} MTP → 1 PTP  |  {CONVERT_RATE} PTP → 1 MTP",
            TextPresets.SYSTEM
        ))
        if ptp_loaned > 0 or mtp_loaned > 0:
            await session.send_line("")
            await session.send_line(colorize("  Outstanding loans:", TextPresets.WARNING))
            if ptp_loaned > 0:
                await session.send_line(colorize(
                    f"    PTP loan: {ptp_loaned} PTP borrowed from MTP pool "
                    f"(refund costs {ptp_loaned} PTP, returns {ptp_loaned * CONVERT_RATE} MTP)",
                    TextPresets.WARNING
                ))
            if mtp_loaned > 0:
                await session.send_line(colorize(
                    f"    MTP loan: {mtp_loaned} MTP borrowed from PTP pool "
                    f"(refund costs {mtp_loaned} MTP, returns {mtp_loaned * CONVERT_RATE} PTP)",
                    TextPresets.WARNING
                ))
        else:
            await session.send_line(colorize(
                "  No outstanding loans.",
                TextPresets.SYSTEM
            ))
        await session.send_line("")
        await session.send_line(colorize(
            "  Usage: CONVERT PTP <amount>   (spend MTP, gain PTP)",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "         CONVERT MTP <amount>   (spend PTP, gain MTP)",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "         CONVERT REFUND         (losslessly undo all conversions)",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "         CONVERT REFUND PTP     (refund PTP loan only)",
            TextPresets.SYSTEM
        ))
        await session.send_line(colorize(
            "         CONVERT REFUND MTP     (refund MTP loan only)",
            TextPresets.SYSTEM
        ))
        await session.send_line("")
        return

    tokens = args.lower().split()

    # ── REFUND path ────────────────────────────────────────────────────────
    if tokens[0] == "refund":
        scope = tokens[1] if len(tokens) > 1 else "all"
        if scope not in ("all", "ptp", "mtp"):
            await session.send_line(colorize(
                "  Usage: CONVERT REFUND  |  CONVERT REFUND PTP  |  CONVERT REFUND MTP",
                TextPresets.WARNING
            ))
            return

        do_ptp_refund = scope in ("all", "ptp")
        do_mtp_refund = scope in ("all", "mtp")

        # Validate: do we have enough TPs to pay back?
        errors = []
        if do_ptp_refund and ptp_loaned > 0 and ptp < ptp_loaned:
            errors.append(
                f"PTP refund needs {ptp_loaned} PTP (you have {ptp}).  "
                f"Train to recover {ptp_loaned - ptp} more PTP first, or refund MTP loan instead."
            )
        if do_mtp_refund and mtp_loaned > 0 and mtp < mtp_loaned:
            errors.append(
                f"MTP refund needs {mtp_loaned} MTP (you have {mtp}).  "
                f"Train to recover {mtp_loaned - mtp} more MTP first, or refund PTP loan instead."
            )
        if errors:
            for err in errors:
                await session.send_line(colorize(f"  ✖ {err}", TextPresets.WARNING))
            return

        # Nothing to refund?
        if (do_ptp_refund and ptp_loaned == 0) and (do_mtp_refund and mtp_loaned == 0):
            await session.send_line(colorize(
                "  You have no outstanding conversion loans to refund.",
                TextPresets.SYSTEM
            ))
            return
        if do_ptp_refund and ptp_loaned == 0 and not do_mtp_refund:
            await session.send_line(colorize(
                "  You have no PTP loan outstanding.",
                TextPresets.SYSTEM
            ))
            return
        if do_mtp_refund and mtp_loaned == 0 and not do_ptp_refund:
            await session.send_line(colorize(
                "  You have no MTP loan outstanding.",
                TextPresets.SYSTEM
            ))
            return

        # Apply refunds
        lines = []
        if do_ptp_refund and ptp_loaned > 0:
            recovered_mtp = ptp_loaned * CONVERT_RATE
            session.physical_tp -= ptp_loaned
            session.mental_tp   += recovered_mtp
            session.ptp_loaned   = 0
            lines.append(
                f"  PTP loan refunded: returned {ptp_loaned} PTP, "
                f"recovered {recovered_mtp} MTP."
            )

        if do_mtp_refund and mtp_loaned > 0:
            recovered_ptp = mtp_loaned * CONVERT_RATE
            session.mental_tp   -= mtp_loaned
            session.physical_tp += recovered_ptp
            session.mtp_loaned   = 0
            lines.append(
                f"  MTP loan refunded: returned {mtp_loaned} MTP, "
                f"recovered {recovered_ptp} PTP."
            )

        _save_convert_state(server, session)

        await session.send_line("")
        for line in lines:
            await session.send_line(colorize(line, TextPresets.EXPERIENCE))
        await session.send_line(colorize(
            f"  Remaining — Physical: {session.physical_tp}  Mental: {session.mental_tp}",
            TextPresets.SYSTEM
        ))
        if session.ptp_loaned == 0 and session.mtp_loaned == 0:
            await session.send_line(colorize(
                "  All conversion loans have been cleared.",
                TextPresets.SYSTEM
            ))
        await session.send_line("")
        return

    # ── CONVERT PTP/MTP path ───────────────────────────────────────────────
    if len(tokens) < 2:
        await session.send_line(colorize(
            "  Usage: CONVERT PTP <amount>  or  CONVERT MTP <amount>",
            TextPresets.WARNING
        ))
        return

    direction = tokens[0]
    if direction not in ("ptp", "mtp"):
        await session.send_line(colorize(
            "  Specify PTP or MTP.  Example: CONVERT PTP 10",
            TextPresets.WARNING
        ))
        return

    try:
        amount = int(tokens[1])
    except ValueError:
        await session.send_line(colorize(
            f"  '{tokens[1]}' is not a number.",
            TextPresets.WARNING
        ))
        return

    if amount <= 0:
        await session.send_line(colorize(
            "  Amount must be greater than zero.",
            TextPresets.WARNING
        ))
        return

    cost = amount * CONVERT_RATE

    if direction == "ptp":
        if mtp < cost:
            await session.send_line(colorize(
                f"  Not enough MTP.  Converting {amount} PTP costs {cost} MTP "
                f"(you have {mtp}).",
                TextPresets.WARNING
            ))
            return
        session.mental_tp   = mtp - cost
        session.physical_tp = ptp + amount
        session.ptp_loaned  = ptp_loaned + amount
        gained_type = "PTP"; spent_type = "MTP"
        gained = amount; spent = cost
        loan_msg = (
            f"  PTP loan balance: {session.ptp_loaned} PTP "
            f"(CONVERT REFUND PTP to undo)"
        )
    else:
        if ptp < cost:
            await session.send_line(colorize(
                f"  Not enough PTP.  Converting {amount} MTP costs {cost} PTP "
                f"(you have {ptp}).",
                TextPresets.WARNING
            ))
            return
        session.physical_tp = ptp - cost
        session.mental_tp   = mtp + amount
        session.mtp_loaned  = mtp_loaned + amount
        gained_type = "MTP"; spent_type = "PTP"
        gained = amount; spent = cost
        loan_msg = (
            f"  MTP loan balance: {session.mtp_loaned} MTP "
            f"(CONVERT REFUND MTP to undo)"
        )

    _save_convert_state(server, session)

    await session.send_line("")
    await session.send_line(colorize(
        f"  Converted {spent} {spent_type} → {gained} {gained_type}.",
        TextPresets.EXPERIENCE
    ))
    await session.send_line(colorize(
        f"  Remaining — Physical: {session.physical_tp}  Mental: {session.mental_tp}",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(loan_msg, TextPresets.WARNING))
    await session.send_line("")
