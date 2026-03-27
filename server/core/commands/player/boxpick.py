"""
Global locksmith queue + GS4-style front-end commands.

Customer-facing flow:
  RING BELL           — Quote box-opening service for the held box
  PAY <amount>        — Accept the current box/repair quote
  APPRAISE <pick>     — Quote lockpick repair at a locksmith

Rogue-facing flow:
  BOXPICK             — View global pending jobs from any locksmith
  CLAIM <#>           — Claim a pending job
  DONE <#>            — Return with the opened box and collect pay

Owner queue flow:
  MYJOBS              — View your jobs, including completed work
  CANCEL <#>          — Cancel an unclaimed job
  FORFEIT <#>         — Rogue abandons a claimed job

The underlying queue is global. Jobs submitted in one city remain visible and
completable from locksmiths in other cities.
"""

import json
import logging
from server.core.protocol.colors import colorize, TextPresets, npc_speech

log = logging.getLogger(__name__)

# House cut retained by the locksmith on completed jobs.
HOUSE_CUT = 0.10

LOCKSMITH_TEMPLATE_IDS = {
    "shind",
    "wl_locksmith_jyhm",
    "tai_locksmith_tai",
    "ti_locksmith_ti",
    "zl_locksmith_zl",
    "cys_locksmith_hihaeim",
    "kf_locksmith_kf",
    "imt_blackfinger",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_locksmith_npc(npc) -> bool:
    """Best-effort locksmith detection without hardcoding a single room."""
    tid = (getattr(npc, "template_id", None) or "").lower().strip()
    if tid in LOCKSMITH_TEMPLATE_IDS:
        return True

    text = " ".join([
        getattr(npc, "name", "") or "",
        getattr(npc, "title", "") or "",
        getattr(npc, "description", "") or "",
    ]).lower()
    return "locksmith" in text or "lockpick" in text


def _get_locksmith_npc(session, server):
    """Return the locksmith NPC in the room, if any."""
    room = getattr(session, "current_room", None)
    if not room or not hasattr(server, "npcs"):
        return None
    for npc in server.npcs.get_npcs_in_room(room.id):
        if _is_locksmith_npc(npc):
            return npc
    return None


def _in_locksmith(session, server):
    """True if the player is currently standing with a locksmith NPC."""
    return _get_locksmith_npc(session, server) is not None


def _locksmith_name(session, server) -> str:
    npc = _get_locksmith_npc(session, server)
    return npc.display_name if npc else "the locksmith"


def _find_box_in_hands(session, target: str):
    """Find a container in either hand by partial name."""
    target = target.lower()
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and item.get("item_type") == "container":
            sn = (item.get("short_name") or "").lower()
            noun = (item.get("noun") or "").lower()
            if target in sn or target in noun:
                return item, slot
    return None, None


def _find_lockpick_in_hands(session, target: str = ""):
    """Find a lockpick in either hand by partial name."""
    search = (target or "").lower().strip()
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if not item:
            continue
        noun = (item.get("noun") or "").lower()
        if noun not in ("lockpick", "pick"):
            continue
        if not search:
            return item, slot
        hay = " ".join([
            item.get("name", ""),
            item.get("short_name", ""),
            noun,
        ]).lower()
        if search in hay:
            return item, slot
    return None, None


def _locksmith_quote_state(session) -> dict:
    state = getattr(session, "_locksmith_quote", None)
    if not isinstance(state, dict):
        state = {}
        setattr(session, "_locksmith_quote", state)
    return state


def _clear_locksmith_quote(session):
    setattr(session, "_locksmith_quote", {})


def _quote_box_fee(box: dict) -> int:
    """Simple single-player fee curve for locksmith service quotes."""
    lock_diff = int(box.get("lock_difficulty", 20) or 20)
    fee = max(100, ((lock_diff + 24) // 25) * 25)
    if box.get("trapped") and not box.get("trap_disarmed"):
        fee += 100
    if (box.get("noun") or "").lower() in ("coffer", "chest"):
        fee += 25
    return fee


def _repair_quote(pick: dict) -> tuple[int, int, str]:
    """Return (repair_cost, restore_level, result_label)."""
    from server.data.items.lockpicks.lockpicks import get_material_data, LOCKPICK_CONDITIONS

    mat = get_material_data(pick)
    base_price = mat.get("price", 100)
    condition = int(pick.get("pick_condition", 5) or 5)
    is_broken = bool(pick.get("is_broken", False) or condition <= 0)

    if is_broken:
        repair_cost = max(50, base_price // 5)
        restore_level = 3
    else:
        repair_cost = max(20, base_price // 10) * max(1, 5 - condition)
        restore_level = 5

    return repair_cost, restore_level, LOCKPICK_CONDITIONS[restore_level]["label"]


def _restore_snapshot_to_inventory(server, character_id, item_snapshot: dict, slot=None):
    """
    Recreate an escrowed item in inventory and persist its runtime extra_data.
    Returns a fresh in-memory item dict or None on failure.
    """
    item_id = item_snapshot.get("item_id", 0)
    if not item_id:
        return None

    inv_id = server.db.add_item_to_inventory(character_id, item_id, slot=slot)
    if not inv_id:
        return None

    restored = dict(item_snapshot)
    restored["inv_id"] = inv_id
    restored["slot"] = slot
    restored["container_id"] = None

    extra = {
        k: v for k, v in restored.items()
        if k not in {
            "inv_id", "item_id", "name", "short_name", "noun", "article",
            "item_type", "weight", "value", "slot", "container_id",
            "description", "material", "color",
        }
    }
    if extra:
        server.db.save_item_extra_data(inv_id, extra)

    return restored


def _db_submit(server, owner_id, owner_name, item, fee):
    """Insert a new pending job. Returns new job id or None."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        item_snapshot = json.dumps({
            k: v for k, v in item.items()
            if k not in ("inv_id",)  # strip live inv_id from snapshot
        })
        cur.execute("""
            INSERT INTO picking_queue
                (owner_id, owner_name, item_id, item_name, item_short_name,
                 item_data, offered_fee, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (
            owner_id, owner_name,
            item.get("item_id", 0),
            item.get("name", "a box"),
            item.get("short_name", "box"),
            item_snapshot,
            fee,
        ))
        return cur.lastrowid
    except Exception as e:
        log.error("picking_queue insert failed: %s", e)
        return None
    finally:
        conn.close()


def _db_get_pending(server):
    """Return all pending jobs."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, owner_name, item_name, item_short_name,
                   offered_fee, status, submitted_at
            FROM picking_queue
            WHERE status = 'pending'
            ORDER BY submitted_at ASC
        """)
        return cur.fetchall()
    except Exception as e:
        log.error("picking_queue fetch failed: %s", e)
        return []
    finally:
        conn.close()


def _db_get_job(server, job_id):
    """Return a single job by id."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM picking_queue WHERE id = %s", (job_id,))
        return cur.fetchone()
    except Exception as e:
        log.error("picking_queue get job failed: %s", e)
        return None
    finally:
        conn.close()


def _db_get_claimer_active(server, claimer_id):
    """Return a rogue's currently claimed (uncompleted) job, if any."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM picking_queue
            WHERE claimer_id = %s AND status = 'claimed'
            LIMIT 1
        """, (claimer_id,))
        return cur.fetchone()
    except Exception as e:
        log.error("picking_queue claimer check failed: %s", e)
        return None
    finally:
        conn.close()


def _db_claim(server, job_id, claimer_id, claimer_name, claimer_inv_id):
    """Transition job to claimed."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE picking_queue
            SET status = 'claimed',
                claimer_id = %s,
                claimer_name = %s,
                claimer_inv_id = %s,
                claimed_at = NOW()
            WHERE id = %s AND status = 'pending'
        """, (claimer_id, claimer_name, claimer_inv_id, job_id))
        return cur.rowcount == 1
    except Exception as e:
        log.error("picking_queue claim failed: %s", e)
        return False
    finally:
        conn.close()


def _db_complete(server, job_id, item_snapshot: dict):
    """Transition job to completed and store the opened box snapshot."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE picking_queue
            SET status = 'completed',
                item_data = %s,
                item_name = %s,
                item_short_name = %s,
                completed_at = NOW()
            WHERE id = %s AND status = 'claimed'
        """, (
            json.dumps({k: v for k, v in item_snapshot.items() if k != "inv_id"}),
            item_snapshot.get("name", "a box"),
            item_snapshot.get("short_name", "box"),
            job_id,
        ))
        return cur.rowcount == 1
    except Exception as e:
        log.error("picking_queue complete failed: %s", e)
        return False
    finally:
        conn.close()


def _db_cancel(server, job_id):
    """Transition job to cancelled."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE picking_queue
            SET status = 'cancelled'
            WHERE id = %s AND status = 'pending'
        """, (job_id,))
        return cur.rowcount == 1
    except Exception as e:
        log.error("picking_queue cancel failed: %s", e)
        return False
    finally:
        conn.close()


def _db_forfeit(server, job_id):
    """Rogue forfeits — mark cancelled so owner can be refunded."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE picking_queue
            SET status = 'cancelled'
            WHERE id = %s AND status = 'claimed'
        """, (job_id,))
        return cur.rowcount == 1
    except Exception as e:
        log.error("picking_queue forfeit failed: %s", e)
        return False
    finally:
        conn.close()


def _db_collect_completed(server, job_id, owner_id):
    """Mark a completed job as collected by its owner."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE picking_queue
            SET status = 'cancelled'
            WHERE id = %s AND owner_id = %s AND status = 'completed'
        """, (job_id, owner_id))
        return cur.rowcount == 1
    except Exception as e:
        log.error("picking_queue collect completed failed: %s", e)
        return False
    finally:
        conn.close()


def _db_get_owner_jobs(server, owner_id):
    """Return an owner's recent jobs, including completed work."""
    conn = server.db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, item_name, offered_fee, status, claimer_name, submitted_at, completed_at
            FROM picking_queue
            WHERE owner_id = %s
              AND status IN ('pending', 'claimed', 'completed')
            ORDER BY
                CASE WHEN status = 'completed' THEN completed_at ELSE submitted_at END DESC
        """, (owner_id,))
        return cur.fetchall()
    except Exception as e:
        log.error("picking_queue owner jobs failed: %s", e)
        return []
    finally:
        conn.close()


def _save_silver(server, session):
    server.db.save_character_resources(
        session.character_id,
        session.health_current, session.mana_current,
        session.spirit_current,
        getattr(session, "stamina_current", 100),
        session.silver,
    )


def _find_session_by_id(server, character_id):
    """Find an online session by character_id."""
    for s in getattr(server, "_sessions", {}).values():
        if getattr(s, "character_id", None) == character_id:
            return s
    return None


async def maybe_handle_locksmith_appraise(session, args, server) -> bool:
    """
    APPRAISE at a locksmith quotes lockpick repair for a held pick.
    Returns True when the locksmith service handled the command.
    """
    if not _in_locksmith(session, server):
        return False

    pick, _ = _find_lockpick_in_hands(session, args.strip())
    if not pick:
        return False

    condition = int(pick.get("pick_condition", 5) or 5)
    is_broken = bool(pick.get("is_broken", False) or condition <= 0)
    if not is_broken and condition >= 5:
        return False

    npc_name = _locksmith_name(session, server)
    repair_cost, restore_level, restore_label = _repair_quote(pick)
    quote = _locksmith_quote_state(session)
    quote.clear()
    quote.update({
        "kind": "repair",
        "inv_id": pick.get("inv_id"),
        "cost": repair_cost,
        "restore_level": restore_level,
    })

    pick_name = colorize(pick.get("short_name", "your lockpick"), TextPresets.ITEM_NAME)
    await session.send_line(
        npc_speech(npc_name, f"examines {pick_name} with a practiced squint.")
    )
    await session.send_line(
        npc_speech(
            npc_name,
            f'says, "I can restore that for {colorize(str(repair_cost) + " silver", TextPresets.ITEM_NAME)}.  '
            f'Pay me that amount and I\'ll return it in {restore_label} condition."'
        )
    )
    return True


async def cmd_ring(session, cmd, args, server):
    """RING [BELL] - Quote locksmith service for the held locked box."""
    if not _in_locksmith(session, server):
        await session.send_line("There is nothing here to ring for locksmith service.")
        return

    target = (args or "").strip().lower()
    if target and "bell" not in target:
        await session.send_line("Ring what?  Try RING BELL.")
        return

    box = session.right_hand if getattr(session, "right_hand", None) and session.right_hand.get("item_type") == "container" else None
    hand = "right_hand" if box else None
    if not box and getattr(session, "left_hand", None) and session.left_hand.get("item_type") == "container":
        box = session.left_hand
        hand = "left_hand"

    if not box:
        await session.send_line("Hold the locked box in one of your hands before ringing the bell.")
        return
    if box.get("opened") and not box.get("is_locked", True):
        await session.send_line("That box is already open.")
        return
    if not box.get("is_locked", True):
        await session.send_line("That does not appear to be locked.")
        return

    fee = _quote_box_fee(box)
    npc_name = _locksmith_name(session, server)
    quote = _locksmith_quote_state(session)
    quote.clear()
    quote.update({
        "kind": "box",
        "inv_id": box.get("inv_id"),
        "hand": hand,
        "cost": fee,
    })

    box_disp = colorize(box.get("short_name", "the box"), TextPresets.ITEM_NAME)
    await session.send_line("You ring the small service bell.")
    await session.send_line(
        npc_speech(
            npc_name,
            f'glances at {box_disp} and says, "I can have that opened for {colorize(str(fee) + " silver", TextPresets.ITEM_NAME)}.  '
            'If that price suits you, PAY the amount and I\'ll put it into the global queue."'
        )
    )


async def cmd_pay(session, cmd, args, server):
    """PAY <amount> - Accept the current locksmith quote."""
    if not _in_locksmith(session, server):
        await session.send_line("There is no locksmith here waiting for payment.")
        return
    if not args or not args.strip().isdigit():
        await session.send_line("Pay how much?")
        return

    amount = int(args.strip())
    quote = _locksmith_quote_state(session)
    if not quote or "kind" not in quote:
        await session.send_line("You have no current locksmith quote to pay.")
        return

    expected = int(quote.get("cost", 0) or 0)
    if amount != expected:
        await session.send_line(f"The quoted amount is {expected} silver.")
        return
    if session.silver < amount:
        await session.send_line(f"You only have {session.silver} silver.")
        return

    npc_name = _locksmith_name(session, server)

    if quote["kind"] == "box":
        inv_id = quote.get("inv_id")
        box = None
        box_slot = None
        for slot in ("right_hand", "left_hand"):
            item = getattr(session, slot, None)
            if item and item.get("inv_id") == inv_id:
                box = item
                box_slot = slot
                break
        if not box:
            _clear_locksmith_quote(session)
            await session.send_line("You are no longer holding the quoted box.")
            return
        if not box.get("is_locked", True):
            _clear_locksmith_quote(session)
            await session.send_line("That box no longer needs locksmith service.")
            return

        existing = _db_get_owner_jobs(server, session.character_id)
        active = [j for j in existing if j["status"] in ("pending", "claimed")]
        if len(active) >= 3:
            await session.send_line("You already have 3 active locksmith jobs in the queue.")
            return

        session.silver -= amount
        _save_silver(server, session)

        setattr(session, box_slot, None)
        if inv_id:
            server.db.remove_item_from_inventory(inv_id)

        job_id = _db_submit(server, session.character_id, session.character_name, box, amount)
        if not job_id:
            session.silver += amount
            _save_silver(server, session)
            restored = _restore_snapshot_to_inventory(server, session.character_id, box, slot=box_slot)
            if restored:
                if box_slot == "right_hand":
                    session.right_hand = restored
                else:
                    session.left_hand = restored
            await session.send_line("Something went wrong and the service request could not be posted.")
            _clear_locksmith_quote(session)
            return

        box_disp = colorize(box.get("short_name", "the box"), TextPresets.ITEM_NAME)
        await session.send_line(
            npc_speech(npc_name, f"takes {box_disp} and notes the job on the board.")
        )
        await session.send_line(
            npc_speech(
                npc_name,
                f'says, "Job #{job_id} is posted.  Any locksmith on the network can hand it off to a rogue now."'
            )
        )
        _clear_locksmith_quote(session)
        return

    if quote["kind"] == "repair":
        inv_id = quote.get("inv_id")
        pick = None
        for slot in ("right_hand", "left_hand"):
            item = getattr(session, slot, None)
            if item and item.get("inv_id") == inv_id:
                pick = item
                break
        if not pick:
            _clear_locksmith_quote(session)
            await session.send_line("You are no longer holding the quoted pick.")
            return

        session.silver -= amount
        _save_silver(server, session)
        pick["pick_condition"] = int(quote.get("restore_level", 5))
        pick["is_broken"] = False
        if pick.get("inv_id"):
            server.db.save_item_extra_data(pick["inv_id"], {
                "pick_condition": pick["pick_condition"],
                "pick_material": pick.get("pick_material", ""),
                "pick_modifier": pick.get("pick_modifier"),
                "is_broken": False,
            })

        await session.send_line(
            npc_speech(npc_name, f"works over {colorize(pick.get('short_name', 'your lockpick'), TextPresets.ITEM_NAME)} with a file and small vise.")
        )
        await session.send_line(
            npc_speech(npc_name, "says, 'There.  It should serve you again.'")
        )
        _clear_locksmith_quote(session)
        return


# ── SUBMIT ────────────────────────────────────────────────────────────────────

async def cmd_submit(session, cmd, args, server):
    """
    SUBMIT <box> [fee]
    Leave a box at the locksmith queue with an offered fee for a rogue.
    """
    if not _in_locksmith(session, server):
        await session.send_line("That service is only available while standing with a locksmith.")
        return

    if not args:
        await session.send_line("Submit what?  SUBMIT <box> [fee]")
        return

    # Parse: "submit coffer 500" or "submit box"
    parts = args.strip().split()
    fee = 0
    if len(parts) >= 2 and parts[-1].isdigit():
        fee = int(parts[-1])
        item_target = " ".join(parts[:-1])
    else:
        item_target = " ".join(parts)

    box, box_slot = _find_box_in_hands(session, item_target)
    if not box:
        await session.send_line("You need to be holding the box in your hand to submit it.")
        return

    if box.get("opened") and not box.get("is_locked", True):
        await session.send_line("That box is already open — there's nothing to pick.")
        return

    if fee < 0:
        await session.send_line("The fee can't be negative.")
        return

    if fee > session.silver:
        await session.send_line(
            f"You don't have enough silver.  You have {session.silver} silver."
        )
        return

    # Check they don't already have too many pending jobs (max 3)
    existing = _db_get_owner_jobs(server, session.character_id)
    active = [j for j in existing if j["status"] in ("pending", "claimed")]
    if len(active) >= 3:
        await session.send_line(
            "You already have 3 boxes in the queue.  Collect them first."
        )
        return

    # Escrow the fee
    session.silver -= fee
    _save_silver(server, session)

    # Remove box from player
    if box_slot in ("right_hand", "left_hand"):
        setattr(session, box_slot, None)
    inv_id = box.get("inv_id")
    if inv_id:
        server.db.remove_item_from_inventory(inv_id)

    # Insert job
    job_id = _db_submit(server, session.character_id, session.character_name, box, fee)
    if not job_id:
        # Refund everything on DB failure
        session.silver += fee
        _save_silver(server, session)
        restored = _restore_snapshot_to_inventory(server, session.character_id, box, slot=box_slot)
        if restored:
            if box_slot == "right_hand":
                session.right_hand = restored
            else:
                session.left_hand = restored
        await session.send_line("Something went wrong — your box was not submitted.  Please try again.")
        return

    box_disp = colorize(box.get("short_name", "the box"), TextPresets.ITEM_NAME)
    npc_name = _locksmith_name(session, server)
    await session.send_line(
        npc_speech(npc_name, f"takes {box_disp} and tucks it behind the counter.")
    )
    await session.send_line(
        npc_speech(npc_name, f"says, 'Job #{job_id} posted.  "
            f"Fee offered: {colorize(str(fee) + ' silver', TextPresets.ITEM_NAME)}.  "
            f"I take a ten-percent cut when it's picked.  "
            f"Type CANCEL {job_id} if you change your mind.'")
    )

    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} submits {box.get('short_name', 'a box')} to the picking queue.",
        exclude=session,
    )


# ── BOXPICK LIST ──────────────────────────────────────────────────────────────

async def cmd_boxpick(session, cmd, args, server):
    """
    BOXPICK              — Show the global locksmith queue + open jobs list.
    BOXPICK LIST         — Same as above.
    """
    if not _in_locksmith(session, server):
        await session.send_line("That service is only available while standing with a locksmith.")
        return

    sep   = colorize("─" * 60, TextPresets.SYSTEM)
    npc_name = _locksmith_name(session, server)
    title = colorize(f"  {npc_name} — Global Lock Service", TextPresets.ROOM_TITLE)

    await session.send_line("")
    await session.send_line(title)
    await session.send_line(sep)
    await session.send_line(
        colorize("  How it works:", TextPresets.SYSTEM)
    )
    await session.send_line(
        "    Customers ring for a quote, then pay to post the job onto the shared locksmith queue."
    )
    await session.send_line(
        "    Any locksmith can see the same queue, and rogues can work jobs from any city."
    )
    await session.send_line("")
    await session.send_line(colorize("  If you have a locked box to open:", TextPresets.SYSTEM))
    await session.send_line(
        f"    {colorize('RING BELL', TextPresets.SYSTEM)}"
        "              — Quote service for the held box."
    )
    await session.send_line(
        f"    {colorize('PAY <amount>', TextPresets.SYSTEM)}"
        "            — Accept the current quote and post the job."
    )
    await session.send_line(
        f"    {colorize('MYJOBS', TextPresets.SYSTEM)}"
        "                — Check your posted and completed jobs."
    )
    await session.send_line("")
    await session.send_line(colorize("  If you are a rogue looking for work:", TextPresets.SYSTEM))
    await session.send_line(
        f"    {colorize('CLAIM <job #>', TextPresets.SYSTEM)}"
        "             — Claim a job and receive the box.  Pick the lock, then:"
    )
    await session.send_line(
        f"    {colorize('DONE <job #>', TextPresets.SYSTEM)}"
        "             — Return here with the opened box to collect your pay."
    )
    await session.send_line(
        f"    {colorize('FORFEIT <job #>', TextPresets.SYSTEM)}"
        "          — Give up on a job.  The owner gets their full fee back."
    )
    await session.send_line(sep)

    # Show open jobs
    jobs = _db_get_pending(server)
    if not jobs:
        await session.send_line(
            colorize("  No jobs in the queue right now.  Check back later.", TextPresets.SYSTEM)
        )
    else:
        await session.send_line(
            colorize(f"  Open jobs  ({len(jobs)} available):", TextPresets.SYSTEM)
        )
        await session.send_line(
            f"    {'Job #':<8} {'Box':<26} {'Posted by':<16} {'Bounty':>10}"
        )
        await session.send_line("    " + "─" * 56)
        for j in jobs:
            fee_str = colorize(f"{j['offered_fee']} silver", TextPresets.ITEM_NAME)
            box_str = colorize(j["item_short_name"][:24], TextPresets.ITEM_NAME)
            await session.send_line(
                f"    {j['id']:<8} {box_str:<36} {j['owner_name']:<16} {fee_str}"
            )
        await session.send_line(
            f"\n    Type {colorize('CLAIM <job #>', TextPresets.SYSTEM)} to claim one."
        )
    await session.send_line("")


# ── CLAIM ─────────────────────────────────────────────────────────────────────

async def cmd_claim(session, cmd, args, server):
    """
    CLAIM <#>
    Rogue takes a pending job from the queue. Box moves to their right hand.
    """
    if not _in_locksmith(session, server):
        await session.send_line("That service is only available while standing with a locksmith.")
        return

    if not args or not args.strip().isdigit():
        await session.send_line("Claim which job?  CLAIM <job number>")
        return

    job_id = int(args.strip())
    job = _db_get_job(server, job_id)
    npc_name = _locksmith_name(session, server)

    if not job:
        await session.send_line(f"Job #{job_id} does not exist.")
        return

    if job["status"] == "completed":
        if job["owner_id"] != session.character_id:
            await session.send_line("Only the owner can collect a completed locksmith job.")
            return

        item_data = json.loads(job["item_data"])
        restored = _restore_snapshot_to_inventory(server, session.character_id, item_data, slot=None)
        if not restored:
            await session.send_line("Something went wrong retrieving your finished box.  Try again.")
            return

        session.inventory.append(restored)
        if not _db_collect_completed(server, job_id, session.character_id):
            if restored in session.inventory:
                session.inventory.remove(restored)
            if restored.get("inv_id"):
                server.db.remove_item_from_inventory(restored["inv_id"])
            await session.send_line("Something went wrong finalizing your pickup.  Try again.")
            return

        box_disp = colorize(restored.get("short_name", job["item_short_name"]), TextPresets.ITEM_NAME)
        await session.send_line(
            npc_speech(npc_name, f"retrieves {box_disp} and hands it over to you.")
        )
        await session.send_line(
            npc_speech(npc_name, f"says, 'Job #{job_id} was finished by {job['claimer_name']}.  Mind the contents.'")
        )
        return

    if job["status"] != "pending":
        await session.send_line(f"Job #{job_id} is not available.")
        return

    if job["owner_id"] == session.character_id:
        await session.send_line("You can't take your own job.")
        return

    # Check rogue doesn't already have an active claim
    active = _db_get_claimer_active(server, session.character_id)
    if active:
        await session.send_line(
            f"You're already working job #{active['id']}.  "
            f"Finish it with DONE {active['id']} before taking another."
        )
        return

    # Need a free hand
    if session.right_hand and session.left_hand:
        await session.send_line("Your hands are full.  Free up a hand first.")
        return

    # Restore item from snapshot
    item_data = json.loads(job["item_data"])
    target_slot = "right_hand" if session.right_hand is None else "left_hand"
    restored = _restore_snapshot_to_inventory(server, session.character_id, item_data, slot=target_slot)
    if not restored:
        await session.send_line("Something went wrong retrieving the box.  Try again.")
        return

    if target_slot == "right_hand":
        session.right_hand = restored
    else:
        session.left_hand = restored

    # Update job record
    ok = _db_claim(server, job_id, session.character_id, session.character_name, restored["inv_id"])
    if not ok:
        # Race condition — someone else claimed it first
        server.db.remove_item_from_inventory(restored["inv_id"])
        if target_slot == "right_hand":
            session.right_hand = None
        else:
            session.left_hand = None
        await session.send_line(f"Job #{job_id} was just taken by someone else.")
        return

    box_disp = colorize(job["item_short_name"], TextPresets.ITEM_NAME)
    fee_disp = colorize(f"{job['offered_fee']} silver", TextPresets.ITEM_NAME)
    await session.send_line(
        npc_speech(npc_name, f"hands you {box_disp} and nods.")
    )
    await session.send_line(
        npc_speech(npc_name, f"says, 'Job #{job_id} for {job['owner_name']}.  "
            f"Fee: {fee_disp}.  PICK the lock, then DONE {job_id} when finished.  "
            f"Or FORFEIT {job_id} if you can't crack it.'")
    )

    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} claims a locksmith job.",
        exclude=session,
    )


# ── DONE ──────────────────────────────────────────────────────────────────────

async def cmd_done(session, cmd, args, server):
    """
    DONE <#>
    Rogue marks a job complete. Box goes back to owner, fee is paid out.
    """
    if not _in_locksmith(session, server):
        await session.send_line("Return to any locksmith to complete a job.")
        return

    if not args or not args.strip().isdigit():
        await session.send_line("Complete which job?  DONE <job number>")
        return

    job_id = int(args.strip())
    job = _db_get_job(server, job_id)

    if not job or job["status"] != "claimed":
        await session.send_line(f"Job #{job_id} is not currently claimed.")
        return

    if job["claimer_id"] != session.character_id:
        await session.send_line("That's not your job.")
        return

    # Find the box in rogue's hands
    box = None
    box_slot = None
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and item.get("inv_id") == job["claimer_inv_id"]:
            box = item
            box_slot = slot
            break
    # Also check inventory
    if not box:
        for item in session.inventory:
            if item.get("inv_id") == job["claimer_inv_id"]:
                box = item
                box_slot = "inventory"
                break

    if not box:
        await session.send_line(
            f"I can't find the box from job #{job_id} on you.  "
            f"Do you still have it?  Use FORFEIT {job_id} if you lost it."
        )
        return

    if box.get("is_locked", True) and not box.get("opened"):
        await session.send_line(
            "That box is still locked.  PICK it first before marking the job done."
        )
        return

    if not _db_complete(server, job_id, box):
        await session.send_line("Something went wrong marking that job complete.  Try again.")
        return

    owner_session = _find_session_by_id(server, job["owner_id"])

    # Remove the box from the rogue only after the completed snapshot is stored.
    if box_slot in ("right_hand", "left_hand"):
        setattr(session, box_slot, None)
    elif box_slot == "inventory" and box in session.inventory:
        session.inventory.remove(box)
    if job["claimer_inv_id"]:
        server.db.remove_item_from_inventory(job["claimer_inv_id"])

    # Calculate payout
    gross_fee = job["offered_fee"]
    house_cut = int(gross_fee * HOUSE_CUT)
    rogue_pay = gross_fee - house_cut

    # Pay rogue
    session.silver += rogue_pay
    _save_silver(server, session)

    box_disp = colorize(job["item_short_name"], TextPresets.ITEM_NAME)
    pay_disp = colorize(f"{rogue_pay} silver", TextPresets.ITEM_NAME)
    cut_disp = colorize(f"{house_cut} silver", TextPresets.ITEM_NAME)

    npc_name = _locksmith_name(session, server)
    await session.send_line(
        npc_speech(npc_name, f"takes {box_disp} and marks job #{job_id} complete for {job['owner_name']}.")
    )
    await session.send_line(
        npc_speech(npc_name, f"says, 'Your cut is {pay_disp}.  Mine is {cut_disp}.  Good work.'")
    )

    # Notify owner if online
    if owner_session:
        await owner_session.send_line(
            colorize(
                f"\n[Picking Queue] {job['item_short_name']} has been picked by "
                f"{session.character_name}.  You can CLAIM {job_id} from any locksmith.",
                TextPresets.SYSTEM
            )
        )

    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} completes a picking job.",
        exclude=session,
    )


# ── CANCEL ────────────────────────────────────────────────────────────────────

async def cmd_cancel_job(session, cmd, args, server):
    """
    CANCEL <#>
    Owner cancels a pending (unclaimed) job. Box and full fee are returned.
    """
    if not _in_locksmith(session, server):
        await session.send_line("Return to any locksmith to cancel a job.")
        return

    if not args or not args.strip().isdigit():
        await session.send_line("Cancel which job?  CANCEL <job number>")
        return

    job_id = int(args.strip())
    job = _db_get_job(server, job_id)

    if not job:
        await session.send_line(f"Job #{job_id} not found.")
        return
    if job["owner_id"] != session.character_id:
        await session.send_line("That's not your job.")
        return
    if job["status"] == "claimed":
        await session.send_line(
            f"Job #{job_id} has already been claimed by {job['claimer_name']}.  "
            "You can't cancel it now — wait for them to finish or forfeit."
        )
        return
    if job["status"] != "pending":
        await session.send_line(f"Job #{job_id} is already {job['status']}.")
        return

    ok = _db_cancel(server, job_id)
    if not ok:
        await session.send_line("Something went wrong.  Try again.")
        return

    item_data = json.loads(job["item_data"])
    restored = _restore_snapshot_to_inventory(server, session.character_id, item_data, slot=None)
    if restored:
        session.inventory.append(restored)

    # Refund full fee
    fee = job["offered_fee"]
    session.silver += fee
    _save_silver(server, session)

    box_disp = colorize(job["item_short_name"], TextPresets.ITEM_NAME)
    npc_name = _locksmith_name(session, server)
    await session.send_line(
        npc_speech(npc_name, f"retrieves {box_disp} from behind the counter and hands it back.")
    )
    if fee:
        await session.send_line(
            npc_speech(npc_name, f"says, 'Job #{job_id} cancelled.  "
                f"Here's your {colorize(str(fee) + ' silver', TextPresets.ITEM_NAME)} back.'")
        )
    else:
        await session.send_line(
            npc_speech(npc_name, f"says, 'Job #{job_id} cancelled.'")
        )


# ── FORFEIT ───────────────────────────────────────────────────────────────────

async def cmd_forfeit(session, cmd, args, server):
    """
    FORFEIT <#>
    Rogue gives up on a claimed job. Owner gets full fee back, rogue gets nothing.
    Box is marked lost (owner must resubmit).
    """
    if not _in_locksmith(session, server):
        await session.send_line("Return to any locksmith to forfeit a job.")
        return

    if not args or not args.strip().isdigit():
        await session.send_line("Forfeit which job?  FORFEIT <job number>")
        return

    job_id = int(args.strip())
    job = _db_get_job(server, job_id)

    if not job or job["status"] != "claimed":
        await session.send_line(f"Job #{job_id} is not currently claimed.")
        return
    if job["claimer_id"] != session.character_id:
        await session.send_line("That's not your job.")
        return

    # Remove box from rogue if they still have it
    claimer_inv_id = job["claimer_inv_id"]
    if claimer_inv_id:
        for slot in ("right_hand", "left_hand"):
            item = getattr(session, slot, None)
            if item and item.get("inv_id") == claimer_inv_id:
                setattr(session, slot, None)
                break
        for item in session.inventory:
            if item.get("inv_id") == claimer_inv_id:
                session.inventory.remove(item)
                break
        server.db.remove_item_from_inventory(claimer_inv_id)

    _db_forfeit(server, job_id)

    # Refund full fee to owner
    fee = job["offered_fee"]
    owner_session = _find_session_by_id(server, job["owner_id"])
    if owner_session:
        owner_session.silver += fee
        server.db.save_character_resources(
            owner_session.character_id,
            owner_session.health_current, owner_session.mana_current,
            owner_session.spirit_current,
            getattr(owner_session, "stamina_current", 100),
            owner_session.silver,
        )
        await owner_session.send_line(
            colorize(
                f"\n[Picking Queue] {session.character_name} has forfeited job #{job_id} "
                f"({job['item_short_name']}).  Your {fee} silver fee has been refunded.  "
                "You will need to resubmit the box.",
                TextPresets.WARNING
            )
        )
    else:
        # Owner offline — update their silver in DB directly
        server.db.execute_query(
            "UPDATE characters SET silver = silver + %s WHERE id = %s",
            (fee, job["owner_id"])
        )

    npc_name = _locksmith_name(session, server)
    await session.send_line(
        npc_speech(npc_name, f"says, 'Job #{job_id} forfeited.  "
            f"The fee has been returned to {job['owner_name']}.  Better luck next time.'")
    )


# ── MYJOBS ────────────────────────────────────────────────────────────────────

async def cmd_myjobs(session, cmd, args, server):
    """
    MYJOBS — Show your own submitted jobs and their status.
    """
    if not _in_locksmith(session, server):
        await session.send_line("That service is only available while standing with a locksmith.")
        return

    jobs = _db_get_owner_jobs(server, session.character_id)
    if not jobs:
        await session.send_line("You have no posted or completed jobs in the locksmith queue.")
        return

    sep = colorize("─" * 55, TextPresets.SYSTEM)
    await session.send_line(f"\n{colorize('Your Picking Jobs', TextPresets.ROOM_TITLE)}")
    await session.send_line(sep)
    for j in jobs:
        status_color = TextPresets.COMBAT_HIT if j["status"] == "completed" else TextPresets.SYSTEM
        status_str = colorize(j["status"].upper(), status_color)
        fee_str = colorize(f"{j['offered_fee']} silver", TextPresets.ITEM_NAME)
        claimer = f"  (claimed by {j['claimer_name']})" if j.get("claimer_name") else ""
        await session.send_line(
            f"  #{j['id']}  {colorize(j['item_name'], TextPresets.ITEM_NAME):<38} "
            f"{fee_str}  [{status_str}]{claimer}"
        )
    await session.send_line(sep)
    await session.send_line(
        "  Use CANCEL <#> to pull back an unclaimed job.  "
        "Use CLAIM <#> to collect a completed box from any locksmith.\n"
    )


# =========================================================
# REPAIR — legacy shortcut for locksmith lockpick repair
# =========================================================

async def cmd_repair(session, cmd, args, server):
    """
    REPAIR <pick> - Have the locksmith repair a broken lockpick.
    Must be at a locksmith.  The pick must be in your hand.
    Cost scales with pick material.  Restores to condition 3 (neglected) —
    not brand new, but usable.  Full restoration to 5 (excellent) costs more.
    """
    if not _in_locksmith(session, server):
        await session.send_line("That service is only available while standing with a locksmith.")
        return

    if not args:
        await session.send_line("Repair what?  Hold the broken pick in your hand.")
        return

    search = args.strip().lower()

    # Find the pick in hands
    pick = None
    hand = None
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and (item.get("noun") or "").lower() in ("lockpick", "pick"):
            if search in (item.get("name") or "").lower() or \
               search in (item.get("short_name") or "").lower() or \
               search in (item.get("noun") or "").lower():
                pick = item
                hand = slot
                break

    if not pick:
        await session.send_line(
            f"You don't have a lockpick matching '{args.strip()}' in your hands."
        )
        return

    condition = pick.get("pick_condition", 5)
    is_broken = pick.get("is_broken", False) or condition <= 0

    if not is_broken and condition >= 5:
        pick_name = colorize(pick.get("short_name") or "your pick", TextPresets.ITEM_NAME)
        npc_name = _locksmith_name(session, server)
        await session.send_line(
            f"{npc_name} examines {pick_name} and shrugs.  "
            "'That pick is in fine condition — doesn't need work.'"
        )
        return

    # Cost calculation based on material
    from server.data.items.lockpicks.lockpicks import get_material_data, LOCKPICK_CONDITIONS
    mat        = get_material_data(pick)
    base_price = mat.get("price", 100)

    if is_broken or condition <= 0:
        # Broken: restore to condition 3 (neglected but usable)
        repair_cost   = max(50, base_price // 5)
        restore_level = 3
        restore_label = LOCKPICK_CONDITIONS[restore_level]["label"]
        action        = "repairs"
        result_msg    = f"restored to {restore_label}"
    else:
        # Damaged but not broken: full restore to 5 (excellent)
        repair_cost   = max(20, base_price // 10) * (5 - condition)
        restore_level = 5
        restore_label = LOCKPICK_CONDITIONS[restore_level]["label"]
        action        = "refurbishes"
        result_msg    = f"restored to {restore_label}"

    pick_name = colorize(pick.get("short_name") or "your pick", TextPresets.ITEM_NAME)
    cost_str  = colorize(str(repair_cost) + " silver", TextPresets.ITEM_NAME)
    npc_name = _locksmith_name(session, server)

    if session.silver < repair_cost:
        await session.send_line(
            f"{npc_name} eyes {pick_name} and shakes his head.  "
            f"'Repair on that'll run you {cost_str}.  "
            f"You only have {session.silver}.  Come back when you're flush.'"
        )
        return

    # Deduct silver and restore pick
    session.silver -= repair_cost
    pick["pick_condition"] = restore_level
    pick["is_broken"]      = False

    inv_id = pick.get("inv_id")
    if inv_id and getattr(server, "db", None) and session.character_id:
        server.db.save_item_extra_data(inv_id, {
            "pick_condition": restore_level,
            "pick_material":  pick.get("pick_material", ""),
            "is_broken":      False,
        })
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver
        )

    await session.send_line(
        f"{npc_name} takes {pick_name}, works it over with a small file and a vise, "
        f"then hands it back.  '{action.capitalize()} the temper.  Good as it's going to get for that price.'"
    )
    await session.send_line(
        colorize(
            f"  {pick_name} has been {result_msg}.  Cost: {repair_cost} silver.",
            TextPresets.COMBAT_HIT
        )
    )
