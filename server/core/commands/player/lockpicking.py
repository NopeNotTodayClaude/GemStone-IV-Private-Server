"""
GemStone IV Lockpicking & Trap System — Full Implementation
PICK and DISARM commands for treasure boxes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PICK formula (wiki-accurate):
  Endroll = (Picking_Locks_skill + DEX_bonus) * pick_modifier - lock_difficulty + d100

  pick_modifier = material modifier * condition modifier_mult
               (copper 1.0 → vaalin 2.5, degrades with condition)

  d100 open rolls: roll of 100 rerolls and adds (cascading)
  d100 = 1 always fumbles regardless of endroll
  endroll > 100 = success
  endroll 81-100 = partial sense → lock_difficulty -5 (stacks, "mod-down")
  endroll 61-80  = "you feel this is within your skill"
  endroll <= 60  = hidden bend roll (may damage/break pick)
  Roundtime: 20s base / 10s at >=150 / 3s at >=200

DISARM formula (wiki-accurate):
  Phase 1 — DETECT: uses Intuition bonus, reveals trap type
  Phase 2 — DISARM: uses DEX bonus, removes trap
  Endroll = (Disarm_Traps_skill + stat_bonus) - trap_difficulty + d100
  d100 <= 8 on phase 2 failure = trap fires

PICK CONDITION SYSTEM:
  5=excellent / 4=good / 3=neglected / 2=damaged / 1=poor / 0=broken
  Each bend reduces condition by 1. Poor → breaks on next bend.
  Persisted to DB via character_inventory.extra_data JSON column.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging
import random
import re
import time as _time
from server.core.protocol.colors import (
    colorize, TextPresets, item_name as fmt_item_name, roundtime_msg
)
from server.core.engine.magic_effects import get_active_buff_totals
from server.core.engine.treasure import TRAP_DEFS
from server.data.items.lockpicks.lockpicks import (
    get_material_data, get_condition, effective_modifier,
    rank_penalty, bend_chance, LOCKPICK_CONDITIONS,
    get_pick_modifier, roll_pick_modifier
)

log = logging.getLogger(__name__)

SKILL_PICKING_LOCKS  = 25
SKILL_DISARMING_TRAPS = 24


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stat_bonus(stat_value: int) -> int:
    return (stat_value - 50) // 2


def _skill_ranks(session, skill_id: int) -> int:
    data = (session.skills or {}).get(skill_id, {})
    return int(data.get("ranks", 0)) if isinstance(data, dict) else 0


def _skill_bonus(session, skill_id: int) -> int:
    ranks = _skill_ranks(session, skill_id)
    return ranks * 3 if ranks else session.level * 2


def _buff_bonus(session, server, key: str) -> int:
    buffs = get_active_buff_totals(server, session)
    return int(buffs.get(key, 0) or 0)


def _rogue_lockmastery_ranks(session) -> int:
    membership = getattr(session, "guild_membership", None) or {}
    if membership.get("guild_id") != "rogue":
        return 0
    row = (getattr(session, "guild_skills", {}) or {}).get("Lock Mastery", {})
    return int(row.get("ranks", 0) or 0)


def _lockmastery_focus_bonus(session, *, consume=False) -> int:
    expires_at = float(getattr(session, "lockmastery_focus_until", 0) or 0)
    if expires_at <= _time.time():
        if hasattr(session, "lockmastery_focus_until"):
            session.lockmastery_focus_until = 0
        return 0
    ranks = _rogue_lockmastery_ranks(session)
    bonus = 10 + max(0, ranks // 8)
    if consume:
        session.lockmastery_focus_until = 0
    return bonus


def _find_box(session, target_name: str):
    """Find a container IN HAND matching target_name.

    DETECT / DISARM / PICK are hand-only operations — the container must be
    held, not buried in a backpack or sitting on the floor.
    An empty target_name matches the first container found in either hand.
    """
    target = _normalize_box_target(target_name)
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and item.get("item_type") == "container":
            # empty target → match whatever container is in hand
            if _box_name_matches(item, target):
                return item, slot
    return None, None


def _normalize_box_target(text: str) -> str:
    raw = str(text or "").strip().lower()
    if not raw:
        return ""
    raw = re.sub(r"\{[^}]+\}", " ", raw)
    raw = raw.replace("â€”", " ").replace("â€œ", " ").replace("â€", " ").replace("â€", " ")
    raw = raw.encode("ascii", "ignore").decode("ascii")
    raw = re.sub(r"[^a-z0-9' -]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw)
    return raw.strip()


def _box_name_matches(item: dict, target: str) -> bool:
    if not target:
        return True
    candidates = [
        item.get("short_name"),
        item.get("name"),
        item.get("base_name"),
        item.get("noun"),
    ]
    target_words = target.split()
    for candidate in candidates:
        normalized = _normalize_box_target(candidate)
        if not normalized:
            continue
        if target == normalized or target in normalized:
            return True
        words = normalized.split()
        if target_words and all(word in words for word in target_words):
            return True
    return False


def _find_lockpick(session):
    """Find a lockpick in either hand."""
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and ((item.get("noun") or "").lower() in ("lockpick", "pick") or item.get("item_type") == "lockpick"):
            return item, slot
    return None, None


def _find_tool_anywhere(session, tool_noun: str):
    item, slot = _find_tool_in_hands(session, tool_noun)
    if item:
        return item, slot, None
    item, toolkit, slot = _find_tool_in_toolkit(session, tool_noun)
    if item:
        return item, slot, toolkit
    return None, None, None


def _lockpick_suggestion(lock_difficulty: int) -> str:
    diff = int(lock_difficulty or 0)
    if diff <= 35:
        return "copper or brass"
    if diff <= 55:
        return "steel or ora"
    if diff <= 75:
        return "mithril or vultite"
    if diff <= 95:
        return "vaalin or kelyn"
    return "your finest precision pick"


async def cmd_lmaster(session, cmd, args, server):
    """LMASTER - Rogue Guild Lock Mastery helper verb."""
    ranks = _rogue_lockmastery_ranks(session)
    if ranks <= 0:
        await session.send_line("You lack the Rogue Guild training to use Lock Mastery techniques.")
        return

    text = (args or "").strip()
    if not text:
        await session.send_line("Use LMASTER with FOCUS, SENSE, CALIPERS <box>, APPRAISE [pick], STOP, or HELP.")
        return

    parts = text.split(None, 1)
    subcmd = parts[0].lower()
    remainder = parts[1] if len(parts) > 1 else ""

    if subcmd == "help":
        await session.send_line("LMASTER FOCUS     - Center yourself for one locksmithing action.")
        await session.send_line("LMASTER SENSE     - Judge room conditions for locksmithing work.")
        await session.send_line("LMASTER CALIPERS <box> - Measure a lock with professional calipers.")
        await session.send_line("LMASTER APPRAISE [pick] - Evaluate a lockpick's material, condition, and reach.")
        await session.send_line("LMASTER STOP      - Clear any held lock mastery focus.")
        return

    if subcmd == "stop":
        session.lockmastery_focus_until = 0
        await session.send_line("You let your lock mastery focus slip away.")
        return

    if subcmd == "focus":
        session.lockmastery_focus_until = _time.time() + 90
        await session.send_line(colorize("You narrow your attention to tumblers, tension, and the slightest give in worked metal.", TextPresets.STEALTH))
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "lm_focus")
        return

    if subcmd == "sense":
        room = getattr(session, "current_room", None)
        if not room:
            await session.send_line("You cannot get a read on your surroundings right now.")
            return
        pieces = []
        if getattr(room, "dark", False):
            pieces.append("The darkness is a locksmith's friend here.")
        elif getattr(room, "indoor", False):
            pieces.append("The indoor light is steady enough for delicate work.")
        else:
            pieces.append("Open air and shifting light will make fine work less comfortable.")
        if getattr(room, "safe", False):
            pieces.append("The room is quiet enough that your hands should stay steady.")
        creatures = server.creatures.get_creatures_in_room(room.id) if hasattr(server, "creatures") else []
        if any(getattr(c, "aggressive", False) and not getattr(c, "is_dead", False) for c in creatures):
            pieces.append("Hostile eyes nearby would make precise locksmithing risky.")
        await session.send_line(" ".join(pieces))
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "lm_sense")
        return

    if subcmd == "calipers":
        tool, _slot, toolkit = _find_tool_anywhere(session, "calipers")
        if not tool:
            await session.send_line("You need professional calipers in hand or in a held toolkit for that.")
            return
        box, _ = _find_box(session, remainder.strip())
        if not box:
            await session.send_line("You need to be holding the container you want to measure.")
            return
        if not box.get("is_locked"):
            await session.send_line("That lock is already open.")
            return
        diff = int(box.get("lock_difficulty", 0) or 0)
        await session.send_line(
            f"You carefully gauge the workings with {fmt_item_name(tool.get('short_name') or 'your calipers')} and judge the lock at difficulty {diff}."
        )
        await session.send_line(f"A { _lockpick_suggestion(diff) } pick looks best suited to it.")
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "lm_calipers")
        return

    if subcmd == "appraise":
        pick, _slot = _find_lockpick(session)
        target = (remainder or "").strip().lower()
        if target:
            for hand in ("right_hand", "left_hand"):
                item = getattr(session, hand, None)
                if item and target in (item.get("short_name", "").lower() or ""):
                    pick = item
                    break
        if not pick or ((pick.get("noun") or "").lower() not in ("lockpick", "pick") and pick.get("item_type") != "lockpick"):
            await session.send_line("You need a lockpick in hand to appraise it with Lock Mastery.")
            return
        if not pick.get("pick_modifier"):
            roll_pick_modifier(pick)
            _save_pick_state(server, session, pick)
        mat = get_material_data(pick)
        cond = get_condition(pick) or {}
        pick_ranks = _skill_ranks(session, SKILL_PICKING_LOCKS)
        await session.send_line(
            f"You study {fmt_item_name(pick.get('short_name') or 'your pick')}: material modifier x{get_pick_modifier(pick):.2f}, condition {cond.get('label', 'good')}."
        )
        await session.send_line(
            f"It carries a rank mismatch penalty of {rank_penalty(pick, pick_ranks)} against your current Picking Locks training."
        )
        return

    await session.send_line("Use LMASTER with FOCUS, SENSE, CALIPERS <box>, APPRAISE [pick], STOP, or HELP.")



def _find_tool_in_hands(session, tool_noun: str):
    """Find a specific tool (by noun) in either hand.
    Returns (item_dict, slot_name) or (None, None).
    """
    noun = tool_noun.lower().strip()
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and (item.get("noun") or "").lower() == noun:
            return item, slot
    return None, None


def _find_tool_in_toolkit(session, tool_noun: str):
    """Find a specific tool inside a toolkit held in either hand.
    The toolkit is a container (item_type='toolkit') that holds disarm tools.
    Returns (tool_item, toolkit_item, toolkit_slot) or (None, None, None).
    """
    noun = tool_noun.lower().strip()
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and item.get("item_type") == "toolkit":
            contents = item.get("contents") or []
            for tool in contents:
                if (tool.get("noun") or "").lower() == noun:
                    return tool, item, slot
    return None, None, None


def _find_disarm_tool(session, tool_noun: str):
    """Find a disarm tool by noun — checks hands first, then inside any held toolkit.
    Returns (tool_item, source_description) or (None, None).
    For consumables (putty/cotton/vials), also checks charges.
    """
    # 1. Direct in hand
    tool, slot = _find_tool_in_hands(session, tool_noun)
    if tool:
        return tool, tool.get("short_name") or tool.get("name") or tool_noun

    # 2. Inside a toolkit in hand
    tool, toolkit, tk_slot = _find_tool_in_toolkit(session, tool_noun)
    if tool:
        return tool, f"{tool.get('short_name', tool_noun)} from your toolkit"

    return None, None


def _consume_charge(tool: dict) -> bool:
    """Consume one charge from a consumable disarm supply (putty, cotton, vials).
    Returns True if charges remain, False if the item is now depleted."""
    charges = tool.get("charges", 100)
    charges -= 1
    tool["charges"] = max(0, charges)
    return charges > 0


_CONSUMABLE_NOUNS = {"putty", "cotton", "vials"}

def _open_roll(base: int) -> tuple[int, int]:
    """
    GS4 open-roll mechanic: d100=100 cascades (reroll + add).
    Returns (final_d100_value, number_of_cascades).
    """
    total  = 0
    cascades = 0
    while True:
        roll = random.randint(1, 100)
        total += roll
        if roll < 100:
            break
        cascades += 1
    return total, cascades


def _save_pick_state(server, session, lockpick: dict):
    """Persist lockpick condition, material, and rolled modifier to DB extra_data."""
    inv_id = lockpick.get("inv_id")
    if inv_id and getattr(server, "db", None) and session.character_id:
        server.db.save_item_extra_data(inv_id, {
            "pick_condition": lockpick.get("pick_condition", 5),
            "pick_material":  lockpick.get("pick_material", ""),
            "pick_modifier":  lockpick.get("pick_modifier"),
        })


def _save_box_state(server, box: dict, **overrides):
    """Persist per-box lock/trap state without dropping related flags."""
    inv_id = box.get("inv_id")
    if not (inv_id and getattr(server, "db", None)):
        return

    extra = {
        "is_locked":       box.get("is_locked", True),
        "opened":          box.get("opened", False),
        "lock_difficulty": box.get("lock_difficulty", 20),
        "trap_type":       box.get("trap_type"),
        "trapped":         box.get("trapped", False),
        "trap_difficulty": box.get("trap_difficulty", 0),
        "trap_checked":    box.get("trap_checked", False),
        "trap_detected":   box.get("trap_detected", False),
        "trap_disarmed":   box.get("trap_disarmed", False),
        "pick_mod_down":   box.get("pick_mod_down", 0),
        "contents":        box.get("contents", []),
    }
    extra.update(overrides)
    server.db.save_item_extra_data(inv_id, extra)


# ── Detect-state cache ──────────────────────────────────────────────────────────
# The box dict is the primary source of truth for trap_detected, but we also
# keep a session-level cache so the state survives if the dict is ever swapped
# (e.g. when an inline item is promoted to a DB-backed item with a new inv_id).

def _box_cache_key(session, box: dict):
    """Stable identifier for this box in the session detect cache."""
    inv_id = box.get("inv_id")
    if inv_id:
        return ("inv", int(inv_id))
    # Fallback: which hand is holding this exact dict?
    for slot in ("right_hand", "left_hand"):
        if getattr(session, slot, None) is box:
            return ("slot", slot)
    return None


def _get_detect_cache(session) -> dict:
    if not hasattr(session, "_trap_detect_cache"):
        session._trap_detect_cache = {}
    return session._trap_detect_cache


def _set_detected(session, box: dict):
    """Mark trap as detected — sets the box dict AND the session cache."""
    box["trap_detected"] = True
    key = _box_cache_key(session, box)
    if key is not None:
        _get_detect_cache(session)[key] = True


def _is_detected(session, box: dict) -> bool:
    """True if this box's trap has been detected in the current session."""
    if box.get("trap_detected"):
        return True
    key = _box_cache_key(session, box)
    if key is not None and _get_detect_cache(session).get(key):
        box["trap_detected"] = True   # re-sync dict from cache
        return True
    return False


def _clear_detected(session, box: dict):
    """Remove a box from the detect cache (called after disarm or trap fire)."""
    key = _box_cache_key(session, box)
    if key is not None:
        _get_detect_cache(session).pop(key, None)


def _bend_pick(server, session, lockpick: dict, endroll: int) -> bool:
    """
    Hidden bend roll after a failed pick.
    Returns True if the pick was damaged or broken (messaging handled here).
    """
    mat      = get_material_data(lockpick)
    strength = mat.get("strength", 2)
    chance   = bend_chance(endroll, strength)
    if random.random() > chance:
        return False  # pick survives

    cond = lockpick.get("pick_condition", 5)

    if cond <= 1:
        # Poor → breaks
        lockpick["pick_condition"] = 0
        _save_pick_state(server, session, lockpick)
        return True   # caller handles removal + messaging
    else:
        lockpick["pick_condition"] = cond - 1
        new_label = LOCKPICK_CONDITIONS[cond - 1]["label"]
        _save_pick_state(server, session, lockpick)
        return False  # bent but not broken — caller shows bend message


async def cmd_detect(session, cmd, args, server):
    """
    DETECT <box> - Thoroughly examine a container.
    Always reveals: lock difficulty tier, whether you can pick it, and the
    minimum d100 roll needed with your current skill and pick.
    Also checks for traps (safe — no risk of firing them).
    """
    if not args:
        await session.send_line("Detect traps on what?")
        return

    box, _ = _find_box(session, args.strip())
    if not box:
        await session.send_line("You need to be holding that in your hands to do that.")
        return

    if box.get("destroyed"):
        await session.send_line("That has been destroyed.")
        return

    disp      = fmt_item_name(box.get("short_name") or "the box")
    trap_type = box.get("trap_type")

    await session.send_line(f"You carefully examine {disp}...")
    focus_bonus = _lockmastery_focus_bonus(session, consume=True)
    if focus_bonus:
        await session.send_line(colorize(f"  Lock Mastery focus steadies your hands and eye.  (+{focus_bonus})", TextPresets.SYSTEM))

    # ── Lock analysis (always shown) ──────────────────────────────────────
    lock_diff  = box.get("lock_difficulty", 0)
    mod_down   = box.get("pick_mod_down", 0)
    eff_diff   = max(1, lock_diff - mod_down)

    if box.get("is_locked"):
        diff_desc = _lock_difficulty_desc(lock_diff)

        # Pick skill with current lockpick
        pick_ranks  = _skill_ranks(session, SKILL_PICKING_LOCKS)
        pick_skill  = (pick_ranks * 3 if pick_ranks else session.level * 2) + focus_bonus
        dex_bonus   = _stat_bonus(getattr(session, "stat_dexterity", 50))

        lockpick, _ = _find_lockpick(session)
        if lockpick:
            # Roll modifier on first use if not yet assigned, then persist it
            if not lockpick.get("pick_modifier"):
                roll_pick_modifier(lockpick)
                _save_pick_state(server, session, lockpick)

            pick_mod        = effective_modifier(lockpick)
            base_mod        = get_pick_modifier(lockpick)
            over_rank_pen   = rank_penalty(lockpick, pick_ranks)
            eff_skill       = max(0, pick_skill + dex_bonus - over_rank_pen)
            pick_name       = lockpick.get("short_name") or "your pick"
            cond            = get_condition(lockpick)
            cond_label      = cond.get("label", "good") if isinstance(cond, dict) else "good"
        else:
            pick_mod        = 1.0
            eff_skill       = pick_skill + dex_bonus
            pick_name       = None
            cond_label      = None

        # Minimum d100 needed: int((eff_skill * pick_mod) - eff_diff + d100) >= 100
        # => d100 >= 100 - int(eff_skill * pick_mod) + eff_diff
        min_roll_needed = 100 - int(eff_skill * pick_mod) + eff_diff

        await session.send_line(colorize(
            f"  Lock: {diff_desc}  (difficulty {lock_diff}"
            + (f", reduced to {eff_diff} from prior attempts" if mod_down else "")
            + ")",
            TextPresets.ITEM_NAME
        ))

        if pick_name:
            await session.send_line(colorize(
                f"  Pick: {pick_name}  [{cond_label}]  (modifier x{base_mod:.2f})",
                TextPresets.SYSTEM
            ))
            await session.send_line(colorize(
                f"  Your skill: {int(eff_skill * pick_mod)} effective vs difficulty {eff_diff}",
                TextPresets.SYSTEM
            ))
        else:
            await session.send_line(colorize(
                "  You have no lockpick in hand — equip one to pick this lock.",
                TextPresets.WARNING
            ))
            await session.send_line(colorize(
                f"  Your skill: {eff_skill} effective vs difficulty {eff_diff}",
                TextPresets.SYSTEM
            ))

        if min_roll_needed <= 1:
            verdict = colorize("  You could pick this in your sleep.  (any roll succeeds)", TextPresets.COMBAT_HIT)
        elif min_roll_needed <= 20:
            verdict = colorize(f"  Very likely.  You need a d100 roll of {min_roll_needed}+ to succeed.", TextPresets.COMBAT_HIT)
        elif min_roll_needed <= 50:
            verdict = colorize(f"  Within reach.  You need a d100 roll of {min_roll_needed}+ to succeed.", TextPresets.SYSTEM)
        elif min_roll_needed <= 80:
            verdict = colorize(f"  Challenging.  You need a d100 roll of {min_roll_needed}+ — consider a better pick or more training.", TextPresets.WARNING)
        elif min_roll_needed <= 100:
            verdict = colorize(f"  Very hard.  You need a d100 roll of {min_roll_needed}+.  An open-roll cascade is your best hope.", TextPresets.WARNING)
        else:
            over = min_roll_needed - 100
            verdict = colorize(
                f"  Out of reach.  Even a perfect d100 roll of 100 leaves you {over} short.  "
                "You need a better pick, more training, or to work it down with partial attempts.",
                TextPresets.WARNING
            )

        await session.send_line(verdict)

    elif box.get("opened"):
        await session.send_line(colorize("  The lock is open.", TextPresets.COMBAT_HIT))
    else:
        await session.send_line(colorize("  This container does not appear to be locked.", TextPresets.SYSTEM))

    # ── Trap analysis ─────────────────────────────────────────────────────
    await session.send_line("")  # blank line separator

    if box.get("trap_disarmed"):
        await session.send_line(colorize("  Trap: already disarmed.", TextPresets.COMBAT_HIT))

    elif not box.get("trapped") or not trap_type:
        box["trap_checked"] = True
        _save_box_state(server, box)
        await session.send_line(colorize("  Trap: none detected.", TextPresets.COMBAT_HIT))

    else:
        box["trap_checked"] = True
        trap = TRAP_DEFS.get(trap_type, TRAP_DEFS["needle"])

        if _is_detected(session, box):
            _save_box_state(server, box)
            await session.send_line(colorize(f"  Trap: {trap['examine']}", TextPresets.WARNING))
            await session.send_line(colorize("  Use DISARM to neutralize it.", TextPresets.SYSTEM))
        else:
            # Detection roll
            dis_skill = (
                _skill_bonus(session, SKILL_DISARMING_TRAPS)
                + _buff_bonus(session, server, "disarming_traps_bonus")
                + focus_bonus
            )
            int_bonus = _stat_bonus(getattr(session, "stat_intuition", 50))
            trap_diff = box.get("trap_difficulty", session.level * 12)
            d100, _   = _open_roll(0)
            endroll   = -999 if d100 == 1 else (dis_skill + int_bonus) - trap_diff + d100

            if endroll >= 0:
                _set_detected(session, box)
                _save_box_state(server, box, trapped=True, trap_detected=True, trap_disarmed=False)
                await session.send_line(colorize(f"  Trap: {trap['examine']}", TextPresets.WARNING))
                await session.send_line(colorize("  Use DISARM to neutralize it.", TextPresets.SYSTEM))
            else:
                _save_box_state(server, box)
                await session.send_line(colorize(
                    "  Trap: you do not detect anything, but something feels off...",
                    TextPresets.SYSTEM
                ))

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))
    if getattr(server, "guild", None):
        await server.guild.record_event(session, "detect_success")


# ── DISARM ────────────────────────────────────────────────────────────────────

async def cmd_disarm(session, cmd, args, server):
    """
    DISARM <box> - Attempt to disarm a detected trap on a container.
    Use DETECT first to find the trap. Each trap type requires a specific tool
    from the locksmith's toolkit. Without the right tool you get a severe penalty.
    Failure with a very low roll fires the trap.
    Uses DEX bonus + Disarming Traps skill.
    """
    if not args:
        await session.send_line("Disarm what?")
        return

    box, _ = _find_box(session, args.strip())
    if not box:
        await session.send_line("You need to be holding that in your hands to do that.")
        return

    if box.get("destroyed"):
        await session.send_line("That has been destroyed.")
        return

    disp      = fmt_item_name(box.get("short_name") or "the box")
    trap_type = box.get("trap_type")

    # Not trapped
    if not box.get("trapped") or not trap_type:
        await session.send_line(f"You attempt to disarm {disp}, but find nothing to disarm.")
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    if box.get("trap_disarmed"):
        await session.send_line("  The trap has already been disarmed.")
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    # ── Detection-state check (GS4: DISARM can be attempted blind, but at penalty) ──
    _blind_penalty = 0
    if not _is_detected(session, box):
        if box.get("trap_checked"):
            # Searched but failed to find — allow with stiff penalty, warn player
            _blind_penalty = 40
            await session.send_line(colorize(
                f"  You haven't located the trap on {disp} — working blind.  (-{_blind_penalty} penalty)",
                TextPresets.WARNING
            ))
        else:
            # Never examined — allow but at maximum penalty, heavy warning
            _blind_penalty = 60
            await session.send_line(colorize(
                f"  You attempt to disarm {disp} without examining it first — working completely blind.  (-{_blind_penalty} penalty)",
                TextPresets.WARNING
            ))

    trap = TRAP_DEFS.get(trap_type, TRAP_DEFS["needle"])
    focus_bonus = _lockmastery_focus_bonus(session, consume=True)
    if focus_bonus:
        await session.send_line(colorize(f"  Lock Mastery focus sharpens each movement.  (+{focus_bonus})", TextPresets.SYSTEM))

    # ── Check for required tools ─────────────────────────────────────────
    required_tools = trap.get("tools", [])
    tool_actions   = trap.get("tool_action", [])
    tool_bonus     = 0
    no_tool_penalty = 0
    found_tools    = []

    if required_tools:
        for i, tool_noun in enumerate(required_tools):
            # Special case: "lockpick" just needs a lockpick in hand
            if tool_noun == "lockpick":
                pick, _ = _find_lockpick(session)
                if pick:
                    found_tools.append((pick, pick.get("short_name", "your lockpick")))
                    tool_bonus += 10
                else:
                    found_tools.append((None, None))
                    no_tool_penalty += 25
                continue

            tool, source = _find_disarm_tool(session, tool_noun)
            if tool:
                found_tools.append((tool, source))
                tool_bonus += 10  # each correct tool gives +10
            else:
                found_tools.append((None, None))
                no_tool_penalty += 25  # each missing tool is -25

        # Show tool usage
        all_found = all(t[0] is not None for t in found_tools)
        if all_found:
            await session.send_line(f"You carefully attempt to disarm the trap on {disp}...")
            for i, (tool, source) in enumerate(found_tools):
                if i < len(tool_actions):
                    await session.send_line(colorize(
                        f"  {tool_actions[i]}",
                        TextPresets.SYSTEM
                    ))
        elif any(t[0] is not None for t in found_tools):
            await session.send_line(f"You attempt to disarm the trap on {disp}, though you're missing some tools...")
            for i, (tool, source) in enumerate(found_tools):
                if tool and i < len(tool_actions):
                    await session.send_line(colorize(
                        f"  {tool_actions[i]}",
                        TextPresets.SYSTEM
                    ))
                elif not tool:
                    await session.send_line(colorize(
                        f"  You don't have the right tool for this step!  (-{25} penalty)",
                        TextPresets.WARNING
                    ))
        else:
            await session.send_line(
                colorize(
                    f"You attempt to disarm the trap on {disp} with your bare hands...",
                    TextPresets.WARNING
                )
            )
            await session.send_line(colorize(
                f"  You don't have any of the tools needed!  (-{no_tool_penalty} penalty)",
                TextPresets.WARNING
            ))
    else:
        # Glyph trap: no tools required, just scrape
        await session.send_line(f"You carefully attempt to disarm the trap on {disp}...")
        await session.send_line(colorize(
            "  You scrape at the markings with your fingernail...",
            TextPresets.SYSTEM
        ))

    # ── Compute endroll ──────────────────────────────────────────────────
    dis_skill  = (
        _skill_bonus(session, SKILL_DISARMING_TRAPS)
        + _buff_bonus(session, server, "disarming_traps_bonus")
        + tool_bonus
        - no_tool_penalty
        + focus_bonus
        - _blind_penalty
    )
    dex_bonus  = _stat_bonus(getattr(session, "stat_dexterity", 50))
    trap_diff  = box.get("trap_difficulty", session.level * 12) + trap["diff_bonus"]

    # Single-player boost: flat +10
    SP_BOOST = 10
    effective = max(0, dis_skill + dex_bonus + SP_BOOST)

    d100, cascades = _open_roll(0)
    fumble     = (d100 == 1)
    endroll    = -99 if fumble else effective - trap_diff + d100

    # Roll math
    roll_math = (
        f"  Skill: {effective}"
        + (f" (tools: +{tool_bonus})" if tool_bonus else "")
        + (f" (no tool: -{no_tool_penalty})" if no_tool_penalty else "")
        + (f" (blind: -{_blind_penalty})" if _blind_penalty else "")
        + f"  -  Trap: {trap_diff}"
        + f"  +  d100: {d100}"
        + f"  =  {'FUMBLE' if fumble else endroll}"
    )

    if cascades:
        await session.send_line(f"  Open roll! (+{cascades * 100} added)  (endroll: {endroll})")

    if not fumble and endroll >= 100:
        # ── Success ──────────────────────────────────────────────────────
        box["trapped"]       = False
        box["trap_disarmed"] = True
        _clear_detected(session, box)
        _save_box_state(server, box, trapped=False, trap_disarmed=True, trap_detected=True)

        await session.send_line(colorize(roll_math, TextPresets.COMBAT_HIT))
        await session.send_line(colorize(
            f"  ...{trap['disarm_msg']}",
            TextPresets.COMBAT_HIT
        ))
        await session.send_line("  The trap has been safely neutralized.")

        # Consume charges from consumable tools
        for tool, source in found_tools:
            if tool and (tool.get("noun") or "").lower() in _CONSUMABLE_NOUNS:
                remaining = _consume_charge(tool)
                if not remaining:
                    await session.send_line(colorize(
                        f"  Your {tool.get('short_name', 'supply')} is now depleted.",
                        TextPresets.WARNING
                    ))

        if session.current_room:
            await server.world.broadcast_to_room(
                session.current_room.id,
                f"{session.character_name} carefully disarms a trap on {box.get('short_name', 'a box')}.",
                exclude=session
            )

        # Award XP for successful disarm
        if hasattr(server, 'experience'):
            await server.experience.award_lockpick_xp(
                session,
                lock_difficulty=trap_diff,
                endroll=endroll
            )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "disarm_success")
    else:
        # ── Failure ──────────────────────────────────────────────────────
        endroll_disp = "fumble!" if fumble else str(endroll)
        await session.send_line(colorize(roll_math, TextPresets.WARNING))
        await session.send_line(colorize(
            f"  ...you fail to disarm the trap.  (endroll: {endroll_disp})",
            TextPresets.WARNING
        ))

        # d100 <= 8 OR fumble fires the trap
        if fumble or d100 <= 8:
            await _trigger_trap(session, server, box, trap)
        else:
            await session.send_line("  You back away carefully without setting it off.")

    session.set_roundtime(4)
    await session.send_line(roundtime_msg(4))

async def _trigger_trap(session, server, box: dict, trap: dict):
    """Fire a trap — deal damage, apply effect, broadcast."""
    box["trapped"] = False
    box["trap_disarmed"] = True
    box["trap_detected"] = True
    _clear_detected(session, box)
    dmg = random.randint(trap["dmg_min"], trap["dmg_max"])
    try:
        from server.core.engine.magic_effects import has_effect
        if trap.get("damage_type") == "poison":
            if has_effect(server, session, "gas_immune"):
                dmg = 0
            elif has_effect(server, session, "poison_resist"):
                dmg = max(0, dmg // 2)
    except Exception:
        pass
    session.health_current = max(0, session.health_current - dmg)

    await session.send_line(colorize(f"  {trap['fail_msg']}", TextPresets.COMBAT_MISS))
    await session.send_line(colorize(
        f"  You take {dmg} points of {trap['damage_type']} damage!",
        TextPresets.WARNING
    ))

    if trap.get("effect"):
        if trap["damage_type"] == "magic":
            drain = dmg // 2
            session.mana_current = max(0, session.mana_current - drain)
            await session.send_line(colorize(f"  {trap['effect']}  ({drain} mana drained)", TextPresets.WARNING))
        elif trap["damage_type"] == "poison":
            # Poison weakens stamina too
            session.stamina_current = max(0, getattr(session, "stamina_current", 100) - dmg // 3)
            await session.send_line(colorize(f"  {trap['effect']}", TextPresets.WARNING))
        else:
            await session.send_line(colorize(f"  {trap['effect']}", TextPresets.WARNING))

    # Boomer destroys the box
    if trap.get("damage_type") == "fire" and trap["dmg_max"] >= 60:
        box["destroyed"] = True
        box["contents"]  = []
        await session.send_line(colorize("  The box is destroyed in the explosion!", TextPresets.WARNING))
    elif not box.get("is_locked"):
        box["opened"] = True

    if session.current_room:
        room_msg = trap["room_msg"].replace("{name}", session.character_name)
        await server.world.broadcast_to_room(
            session.current_room.id,
            colorize(room_msg, TextPresets.WARNING),
            exclude=session
        )

    if getattr(server, "db", None) and session.character_id:
        _save_box_state(server, box)
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current,
            getattr(session, "stamina_current", 100),
            session.silver
        )


# ── PICK ──────────────────────────────────────────────────────────────────────

async def cmd_pick(session, cmd, args, server):
    """PICK <box> - Attempt to pick a lock on a container."""
    if not args:
        await session.send_line("Pick what?")
        return

    box, _ = _find_box(session, args.strip())
    if not box:
        await session.send_line("You need to be holding that in your hands to do that.")
        return

    if box.get("destroyed"):
        await session.send_line("That has been destroyed.")
        return

    if box.get("opened"):
        await session.send_line("That is already open.")
        return

    if not box.get("is_locked"):
        await session.send_line("That does not appear to be locked.")
        box["opened"] = True
        await session.send_line(f"You open {fmt_item_name(box.get('short_name', 'the box'))}.")
        await _show_contents(session, box)
        return

    # Warn if trapped and not yet disarmed
    if box.get("trapped") and not box.get("trap_disarmed"):
        await session.send_line(colorize(
            "  Warning: you sense something is off about this box — you should DISARM it first!",
            TextPresets.WARNING
        ))

    # ── Locate lockpick ───────────────────────────────────────────────────
    lockpick, pick_slot = _find_lockpick(session)

    if not lockpick:
        await session.send_line("You need a lockpick in hand to attempt that.")
        return

    # Seed condition if new pick (just picked up, no condition set yet)
    if "pick_condition" not in lockpick:
        lockpick["pick_condition"] = 5

    # Roll this pick's specific modifier if not yet assigned, then persist
    if not lockpick.get("pick_modifier"):
        roll_pick_modifier(lockpick)
        _save_pick_state(server, session, lockpick)

    if lockpick.get("pick_condition", 5) <= 0:
        await session.send_line(colorize(
            f"  {fmt_item_name(lockpick.get('short_name', 'your lockpick'))} is broken.  "
            "Take it to Shind — use REPAIR <pick> to have it fixed.",
            TextPresets.WARNING
        ))
        return

    focus_bonus = _lockmastery_focus_bonus(session, consume=True)
    if focus_bonus:
        await session.send_line(colorize(f"  Lock Mastery focus settles into the pick.  (+{focus_bonus})", TextPresets.SYSTEM))

    # ── Compute endroll ───────────────────────────────────────────────────
    pick_ranks = _skill_ranks(session, SKILL_PICKING_LOCKS)
    pick_skill = (pick_ranks * 3 if pick_ranks else session.level * 2) + _buff_bonus(session, server, "picking_locks_bonus")
    dex_bonus  = _stat_bonus(getattr(session, "stat_dexterity", 50))
    lock_diff  = box.get("lock_difficulty", session.level * 15 + 20)

    # Apply accumulated mod-down bonus
    mod_down = box.get("pick_mod_down", 0)
    lock_diff = max(1, lock_diff - mod_down)

    # Material modifier × condition
    pick_modifier = effective_modifier(lockpick)

    # Rank requirement penalty
    over_rank_penalty = rank_penalty(lockpick, pick_ranks)

    # Slight single-player boost: flat +10 to base skill before modifier
    SP_BOOST = 10
    effective_skill = max(0, pick_skill + dex_bonus + SP_BOOST + focus_bonus - over_rank_penalty)

    # Open roll for d100 (cascading 100s)
    d100, cascades = _open_roll(0)
    fumble         = (d100 == 1) and (cascades == 0)

    if fumble:
        raw_endroll = -99
    else:
        raw_endroll = int(effective_skill * pick_modifier) - lock_diff + d100

    # Roll math string shown on every attempt (GS4-style breakdown)
    skill_after_mod = int(effective_skill * pick_modifier)
    roll_math = (
        f"  Skill: {effective_skill} x{pick_modifier:.2f} = {skill_after_mod}"
        f"  -  Lock: {lock_diff}"
        f"  +  d100: {d100}"
        f"  =  {raw_endroll if not fumble else 'FUMBLE'}"
    )

    disp = fmt_item_name(box.get("short_name") or "the box")
    mat  = get_material_data(lockpick)
    cond = get_condition(lockpick)

    await session.send_line(f"You settle into the difficult task of picking the lock on {disp}...")

    # ── Rank penalty messaging ────────────────────────────────────────────
    if over_rank_penalty > 0:
        await session.send_line(colorize(
            f"  The {mat.get('precision', '')} pick feels unwieldy in your hands.  (-{over_rank_penalty} to skill)",
            TextPresets.WARNING
        ))

    # ── Open roll messaging ───────────────────────────────────────────────
    if cascades:
        await session.send_line(f"  Open roll! (d100 cascaded {cascades} time{'s' if cascades > 1 else ''}, total +{d100})")

    # ── Fumble ────────────────────────────────────────────────────────────
    if fumble:
        await session.send_line(colorize(roll_math, TextPresets.WARNING))
        await session.send_line(colorize(
            "  You fumble badly with the pick!  (d100=1)",
            TextPresets.WARNING
        ))
        broken = _bend_pick(server, session, lockpick, -99)
        if broken:
            await _break_pick(session, server, lockpick, pick_slot)
        else:
            new_cond = LOCKPICK_CONDITIONS[lockpick.get("pick_condition", 5)]
            await session.send_line(colorize(
                f"  Your lockpick bends!  It is now {new_cond['label']}.",
                TextPresets.WARNING
            ))
        session.set_roundtime(5)
        await session.send_line(roundtime_msg(5))
        return

    # ── Success ───────────────────────────────────────────────────────────
    if raw_endroll >= 100:
        box["is_locked"] = False
        box["pick_mod_down"] = 0  # reset mod-down
        trapped_but_live = box.get("trapped") and not box.get("trap_disarmed")
        box["opened"] = False if trapped_but_live else True

        inv_id = box.get("inv_id")
        if inv_id and getattr(server, "db", None):
            _save_box_state(server, box, is_locked=False, opened=box["opened"], pick_mod_down=0)

        rt = 5
        if raw_endroll >= 200: rt = 1
        elif raw_endroll >= 150: rt = 3

        await session.send_line(colorize(roll_math, TextPresets.COMBAT_HIT))
        if raw_endroll < 150:
            diff_desc = _lock_difficulty_desc(lock_diff)
            await session.send_line(
                f"  You get a sense the lock has a {diff_desc} (-{lock_diff} difficulty).  "
                f"Then...CLICK!  It opens!"
            )
        else:
            await session.send_line(colorize(
                f"  CLICK!  The lock springs open.",
                TextPresets.COMBAT_HIT
            ))

        if trapped_but_live:
            await session.send_line(colorize(
                "  The lock yields, but the trap is still armed.  DISARM it before you dare open the lid.",
                TextPresets.WARNING
            ))
        else:
            await _show_contents(session, box)

        # ── Award XP for successful lockpick ─────────────────────────────
        if hasattr(server, 'experience'):
            await server.experience.award_lockpick_xp(
                session,
                lock_difficulty=box.get("lock_difficulty", 20),
                endroll=raw_endroll
            )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "pick_success")

        if session.current_room:
            await server.world.broadcast_to_room(
                session.current_room.id,
                f"{session.character_name} picks the lock on {box.get('short_name', 'a box')}.",
                exclude=session
            )

        session.set_roundtime(rt)
        await session.send_line(roundtime_msg(rt))

    # ── Partial sense (81–100) — mod-down ─────────────────────────────────
    elif raw_endroll >= 81:
        box["pick_mod_down"] = mod_down + 5
        inv_id = box.get("inv_id")
        if inv_id and getattr(server, "db", None):
            _save_box_state(server, box, opened=False, pick_mod_down=mod_down + 5)
        diff_desc = _lock_difficulty_desc(lock_diff)
        await session.send_line(colorize(roll_math, TextPresets.SYSTEM))
        await session.send_line(
            f"  You get a sense the lock has a {diff_desc} (-{lock_diff} difficulty ranking).  "
            f"You focus in on the lock — it seems slightly easier now."
        )
        session.set_roundtime(5)
        await session.send_line(roundtime_msg(5))

    # ── Feel (61–80) ──────────────────────────────────────────────────────
    elif raw_endroll >= 61:
        await session.send_line(colorize(roll_math, TextPresets.SYSTEM))
        await session.send_line(
            f"  You feel this lock is within your skill, but fail to open it."
        )
        session.set_roundtime(5)
        await session.send_line(roundtime_msg(5))

    # ── Failure (≤ 60) — potential bend ───────────────────────────────────
    else:
        await session.send_line(colorize(roll_math, TextPresets.WARNING))
        await session.send_line(colorize(
            f"  You fail to pick the lock.",
            TextPresets.WARNING
        ))

        prev_cond = lockpick.get("pick_condition", 5)
        broken = _bend_pick(server, session, lockpick, raw_endroll)
        if broken:
            await _break_pick(session, server, lockpick, pick_slot)
        elif lockpick.get("pick_condition", 5) < prev_cond:
            new_label = LOCKPICK_CONDITIONS.get(lockpick.get("pick_condition", 5), {}).get("label", "")
            if new_label:
                await session.send_line(colorize(
                    f"  Your lockpick bends slightly — it is now {new_label}.",
                    TextPresets.WARNING
                ))

        session.set_roundtime(5)
        await session.send_line(roundtime_msg(5))


async def _break_pick(session, server, lockpick: dict, pick_slot: str):
    """Handle a broken lockpick — mark it as broken (condition 0) and leave it
    in the player's hand so they can take it to Shind for repair."""
    name = fmt_item_name(lockpick.get("short_name") or "your lockpick")
    await session.send_line(colorize(f"  {name} snaps!", TextPresets.WARNING))
    await session.send_line(colorize(
        "  It is now broken.  Take it to a locksmith — Shind can repair it with REPAIR <pick>.",
        TextPresets.SYSTEM
    ))

    # Mark broken in the session dict and DB — keep it in hand
    lockpick["pick_condition"] = 0
    lockpick["is_broken"]      = True
    inv_id = lockpick.get("inv_id")
    if inv_id and getattr(server, "db", None) and session.character_id:
        server.db.save_item_extra_data(inv_id, {
            "pick_condition": 0,
            "pick_material":  lockpick.get("pick_material", ""),
            "is_broken":      True,
        })


async def _show_contents(session, box: dict):
    """Show box contents immediately after opening."""
    contents = box.get("contents", [])
    if not contents:
        await session.send_line(
            f"  Looking inside {fmt_item_name(box.get('short_name', 'the box'))}... it is empty."
        )
        return
    await session.send_line(f"  Looking inside {fmt_item_name(box.get('short_name', 'the box'))}:")
    for item in contents:
        await session.send_line(f"    {colorize(item['name'], TextPresets.ITEM_NAME)}")


def _lock_difficulty_desc(difficulty: int) -> str:
    """Return a thief-lingo difficulty description matching GS4 style."""
    if difficulty <= 30:   return "simple"
    if difficulty <= 60:   return "basic"
    if difficulty <= 100:  return "moderately well-crafted"
    if difficulty <= 150:  return "well-crafted"
    if difficulty <= 200:  return "complex"
    if difficulty <= 300:  return "intricate"
    if difficulty <= 400:  return "masterwork"
    return "fiendishly complex"
