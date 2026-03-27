"""
Guild commands - membership, access, and task training.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

from server.core.protocol.colors import colorize, TextPresets, npc_speech


_SUPPORTED_OPTIONS = (
    "status", "menu", "join", "pay", "checkin", "rank", "skills", "task", "practice",
    "complete", "quest", "quests", "vouchers", "swap", "abandon", "password", "invite", "initiate",
    "nominate", "promote", "resign"
)
_MONTH_DAYS = 30
_CHECKIN_DAYS = 90


def _utcnow():
    return datetime.utcnow()


def _as_dt(raw):
    if isinstance(raw, datetime):
        return raw
    return None


def _refresh_guild_state(session, server):
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        session.guild_membership = None
        session.guild_skills = {}
        session.guild_tasks = []
        return

    membership = server.db.get_character_guild_membership(session.character_id)
    session.guild_membership = membership
    if membership:
        guild_id = membership["guild_id"]
        session.guild_skills = server.db.get_character_guild_skills(session.character_id, guild_id)
        session.guild_tasks = server.db.get_character_guild_tasks(session.character_id, guild_id)
    else:
        session.guild_skills = {}
        session.guild_tasks = []


def _get_profession_guild(session, server):
    if not getattr(server, "db", None):
        return None
    return server.db.get_guild_definition_for_profession(getattr(session, "profession_id", 0) or 0)


def _get_room_registry(session, server):
    if not getattr(server, "db", None) or not getattr(session, "current_room", None):
        return []
    try:
        return server.db.get_guild_registry_for_room(session.current_room.id)
    except Exception:
        return []


def _get_local_authority(session, server, guild_id=None):
    room_entries = _get_room_registry(session, server)
    room_npcs = {}
    if hasattr(server, "npcs") and getattr(session, "current_room", None):
        for npc in server.npcs.get_npcs_in_room(session.current_room.id):
            room_npcs[getattr(npc, "template_id", "")] = npc

    for entry in room_entries:
        if guild_id and entry.get("guild_id") != guild_id:
            continue
        npc = room_npcs.get(entry.get("npc_template_id"))
        if npc:
            return entry, npc

    if guild_id:
        for npc in room_npcs.values():
            if getattr(npc, "guild_id", None) == guild_id:
                return None, npc
    return None, None


def _guild_summary_line(membership):
    guild_name = membership.get("guild_name", "Unknown Guild")
    rank_name = membership.get("rank_name") or "Member"
    return f"You are a {rank_name} of the {guild_name}."


def _dues_status_line(membership):
    now = _utcnow()
    dues_paid_through = _as_dt(membership.get("dues_paid_through"))
    monthly_dues = int(membership.get("monthly_dues") or 0)

    if int(membership.get("is_guildmaster", 0) or 0):
        return "As a guildmaster, you do not owe monthly dues."
    if monthly_dues <= 0:
        return "Your guild currently does not require monthly dues."
    if not dues_paid_through:
        return "Your dues are not current.  Use GLD PAY while speaking to a local guild authority."
    if dues_paid_through >= now:
        days = max(0, (dues_paid_through - now).days)
        return f"Your dues are current for another {days} day{'s' if days != 1 else ''}."
    days = max(0, (now - dues_paid_through).days)
    return f"Your dues are overdue by {days} day{'s' if days != 1 else ''}.  Use GLD PAY to catch up."


def _checkin_status_line(membership):
    now = _utcnow()
    due_at = _as_dt(membership.get("next_checkin_due_at"))
    if int(membership.get("is_guildmaster", 0) or 0):
        if not due_at:
            return "As a guildmaster, you still need to check in monthly."
        if due_at >= now:
            days = max(0, (due_at - now).days)
            return f"As a guildmaster, you must check in again within {days} day{'s' if days != 1 else ''}."
        days = max(0, (now - due_at).days)
        return f"Your guildmaster registration is overdue for check-in by {days} day{'s' if days != 1 else ''}."
    if not due_at:
        return "You have not checked in with your guild yet."
    if due_at >= now:
        days = max(0, (due_at - now).days)
        return f"You must check in again within {days} day{'s' if days != 1 else ''}."
    days = max(0, (now - due_at).days)
    return f"You are overdue for a guild check-in by {days} day{'s' if days != 1 else ''}."


def _total_guild_ranks(session):
    total = 0
    for row in (getattr(session, "guild_skills", {}) or {}).values():
        ranks = int(row.get("ranks", 0) or 0)
        if ranks > 0:
            total += max(0, ranks - 1)
    return total


def _guild_cap_line(membership, session):
    total = _total_guild_ranks(session)
    if total <= 0:
        return "You currently have 0 recorded guild skill ranks."
    return f"You currently have {total} total guild skill ranks recorded."


def _voucher_line(membership):
    vouchers = int(membership.get("vouchers", 0) or 0)
    return f"You currently have {vouchers} task trading voucher{'s' if vouchers != 1 else ''}."


def _guild_multiplier_line(membership):
    mult = float(membership.get("progression_multiplier") or 1.0)
    return f"Guild task progression is currently running at {mult:.2f}x speed."


def _support_line(membership):
    support = (membership.get("support_level") or "").lower()
    if support == "complete":
        return "This guild is flagged as a complete profession guild."
    if support == "incomplete":
        return "This guild has partial skill support.  Membership and dues are live, but deeper task training still needs its backend."
    return "This guild currently has social/building support only.  Skill training is not available."


def _find_room_player(session, server, target_name):
    room = getattr(session, "current_room", None)
    if not room:
        return None
    target_l = (target_name or "").strip().lower()
    for other in server.world.get_players_in_room(room.id):
        if other is session:
            continue
        if (getattr(other, "character_name", "") or "").lower() == target_l:
            return other
    return None


async def _show_menu(session):
    await session.send_line(colorize("Guild commands:", TextPresets.SYSTEM))
    await session.send_line("  GLD              - View your guild status")
    await session.send_line("  GLD MENU         - Show this command list")
    await session.send_line("  GLD JOIN         - Join your profession guild or request rogue entry access")
    await session.send_line("  GLD PAY [months] - Pay 1-3 months of guild dues")
    await session.send_line("  GLD CHECKIN      - Check in with your guild once dues are current")
    await session.send_line("  GLD RANK         - View your current guild rank")
    await session.send_line("  GLD SKILLS       - Show your guild skill ranks and training progress")
    await session.send_line("  GLD TASK [skill] - Get or review your active guild task")
    await session.send_line("  GLD PRACTICE     - Work one step of a practice-room guild task")
    await session.send_line("  GLD COMPLETE     - Turn in a completed guild task")
    await session.send_line("  GLD QUESTS       - Review your rogue guild quest journal")
    await session.send_line("  GLD QUEST START  - Begin your next rogue guild quest")
    await session.send_line("  GLD QUEST HINT   - Review your active rogue guild quest hint")
    await session.send_line("  GLD VOUCHERS     - View your task trading vouchers")
    await session.send_line("  GLD SWAP [skill] - Spend a voucher to trade your current task")
    await session.send_line("  GLD ABANDON      - Abandon your current guild task")
    await session.send_line("  GLD PASSWORD     - Review or reissue the rogue entry sequence")
    await session.send_line("  GLD INVITE <who> - Guildmaster invitation for a guild candidate")
    await session.send_line("  GLD INITIATE <who> - Guildmaster-led induction into the guild")
    await session.send_line("  GLD NOMINATE <who> - Nominate an eligible member for guildmaster")
    await session.send_line("  GLD PROMOTE ...  - Promote a guild skill or guildmaster office")
    await session.send_line("  GLD RESIGN       - Resign from your profession guild")


async def _show_status(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        prof_guild = _get_profession_guild(session, server)
        if prof_guild:
            await session.send_line(f"You are not currently a member of the {prof_guild['name']}.")
            if prof_guild.get("guild_id") == "rogue" and getattr(server, "guild", None):
                access = server.guild.get_access_row(session.character_id, "rogue") or {}
                if access.get("is_invited"):
                    await session.send_line(
                        "You have a standing rogue invitation.  In the Ta'Vaalor alley, LEAN first and then use the pass sequence."
                    )
                else:
                    await session.send_line("Visit a local guild authority and use GLD JOIN once you are eligible.")
            else:
                await session.send_line("Visit a local guild authority and use GLD JOIN once you are eligible.")
        else:
            await session.send_line("Your profession does not currently have a supported guild in this build.")
        await session.send_line("Type GLD MENU for available guild commands.")
        return

    await session.send_line(_guild_summary_line(membership))
    await session.send_line(_dues_status_line(membership))
    await session.send_line(_checkin_status_line(membership))
    await session.send_line(_voucher_line(membership))
    await session.send_line(_guild_cap_line(membership, session))
    await session.send_line(_guild_multiplier_line(membership))
    await session.send_line(_support_line(membership))
    if int(membership.get("is_guildmaster", 0) or 0):
        await session.send_line("You currently hold the office of guildmaster.")
    if membership.get("guild_id") == "rogue" and getattr(server, "guild", None):
        password_text = server.guild.get_password_text("rogue")
        if password_text:
            await session.send_line(f"Your rogue entry sequence is {password_text}.")
    tasks = getattr(session, "guild_tasks", []) or []
    if tasks:
        await session.send_line(_active_task_line(tasks[0]))
    if membership.get("guild_id") == "rogue" and getattr(server, "guild", None):
        active_quest = server.guild.get_active_quest(session.character_id, "rogue")
        if active_quest:
            await session.send_line(_active_quest_line(active_quest))
    await session.send_line("Type GLD MENU for available guild commands.")


async def _cmd_rank(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    rank_name = membership.get("rank_name") or "Member"
    rank_level = int(membership.get("rank_level") or 1)
    await session.send_line(
        f"Your current guild rank is {rank_name} (rank level {rank_level}) in the {membership.get('guild_name', 'Unknown Guild')}."
    )
    await session.send_line(_guild_cap_line(membership, session))


async def _cmd_join(session, server):
    if not getattr(server, "db", None):
        await session.send_line("The guild system is unavailable right now.")
        return

    _refresh_guild_state(session, server)
    existing = getattr(session, "guild_membership", None)
    if existing:
        await session.send_line(f"You are already a member of the {existing.get('guild_name', 'guild')}.")
        return

    guild_def = _get_profession_guild(session, server)
    if not guild_def:
        await session.send_line("Your profession does not currently have a supported guild in this build.")
        return

    join_level = int(guild_def.get("join_level") or 15)
    if int(getattr(session, "level", 0) or 0) < join_level:
        await session.send_line(
            f"You must reach level {join_level} before you can join the {guild_def.get('name', 'guild')}."
        )
        return

    authority, npc = _get_local_authority(session, server, guild_def["guild_id"])
    if not npc and guild_def.get("guild_id") == "rogue" and getattr(server, "guild", None):
        access_point = server.guild.get_access_point_for_entry_room("rogue", getattr(session.current_room, "id", 0))
        if access_point:
            if server.guild.issue_remote_invite(
                session.character_id,
                "rogue",
                notes=f"Remote rogue guild invite issued in room {session.current_room.id}.",
            ):
                await session.send_line(
                    "A discreet invitation is now recorded for you.  In this alley, LEAN first and then use the pass sequence: PULL, PULL, SLAP, RUB, RUB, PUSH, TURN."
                )
            else:
                await session.send_line("The rogue network fails to pass your invitation along right now.")
            return
    if not npc:
        await session.send_line(
            f"You need to be at a local {guild_def.get('name', 'guild')} authority before you can join."
        )
        return

    initiation_fee = int(guild_def.get("initiation_fee") or 0)
    if int(getattr(session, "silver", 0) or 0) < initiation_fee:
        await session.send_line(
            npc_speech(npc.display_name, f'says, "The initiation fee is {initiation_fee} silver, and you do not have enough."')
        )
        return

    if initiation_fee > 0:
        session.silver -= initiation_fee
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver,
        )

    notes = f"Joined at room {session.current_room.id}."
    if not server.db.join_guild_member(
        session.character_id,
        guild_def["guild_id"],
        actor_template_id=getattr(npc, "template_id", None),
        notes=notes,
    ):
        await session.send_line("The guild ledger refuses to cooperate right now.")
        return

    if guild_def.get("guild_id") == "rogue" and getattr(server, "guild", None):
        server.guild.grant_member_access(
            session.character_id,
            "rogue",
            actor_template_id=getattr(npc, "template_id", None),
        )

    _refresh_guild_state(session, server)
    if guild_def.get("guild_id") == "rogue" and getattr(server, "guild", None):
        await server.guild.record_event(session, "guild_join_rogue")
    await session.send_line(
        npc_speech(
            npc.display_name,
            f'says, "Welcome to the {guild_def["name"]}.  Your membership is recorded."'
        )
    )
    if initiation_fee > 0:
        await session.send_line(
            colorize(f"  You pay {initiation_fee} silver in initiation fees.", TextPresets.ITEM_NAME)
        )
    if int(guild_def.get("monthly_dues") or 0) > 0:
        await session.send_line(
            "Your first month of dues is not yet paid.  Use GLD PAY while speaking to a guild authority."
        )
    await session.send_line(_support_line(session.guild_membership))


async def _cmd_pay(session, args, server):
    if not getattr(server, "db", None):
        await session.send_line("The guild system is unavailable right now.")
        return

    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    authority, npc = _get_local_authority(session, server, membership["guild_id"])
    if not npc:
        await session.send_line("You must be with a local guild authority to pay guild dues.")
        return

    try:
        months = int((args or "1").strip() or "1")
    except ValueError:
        await session.send_line("GLD PAY expects a number of months, such as GLD PAY 1 or GLD PAY 2.")
        return
    if months < 1:
        await session.send_line("You must pay at least one month of dues.")
        return

    max_prepay = int(membership.get("max_prepay_months") or 3)
    if months > max_prepay:
        await session.send_line(f"You may only pay up to {max_prepay} months at a time.")
        return

    monthly_dues = int(membership.get("monthly_dues") or 0)
    if monthly_dues <= 0:
        await session.send_line(f"The {membership.get('guild_name', 'guild')} does not currently require monthly dues.")
        return

    now = _utcnow()
    current_until = _as_dt(membership.get("dues_paid_through"))
    baseline = current_until if current_until and current_until > now else now
    prepaid_days = max(0, (baseline - now).days)
    prepaid_months = int(math.ceil(prepaid_days / _MONTH_DAYS)) if prepaid_days > 0 else 0
    available_months = max(0, max_prepay - prepaid_months)
    if months > available_months:
        await session.send_line(
            f"You may only add {available_months} more month{'s' if available_months != 1 else ''} of prepayment right now."
        )
        return

    amount = monthly_dues * months
    if int(getattr(session, "silver", 0) or 0) < amount:
        await session.send_line(
            npc_speech(npc.display_name, f'says, "That will be {amount} silver, and you do not have enough."')
        )
        return

    new_due_date = baseline + timedelta(days=_MONTH_DAYS * months)
    session.silver -= amount
    server.db.save_character_resources(
        session.character_id,
        session.health_current, session.mana_current,
        session.spirit_current, session.stamina_current,
        session.silver,
    )
    note = f"Paid {months} month(s) of dues in room {session.current_room.id}."
    if not server.db.pay_guild_dues(
        session.character_id,
        membership["guild_id"],
        new_due_date,
        amount,
        months,
        actor_template_id=getattr(npc, "template_id", None),
        notes=note,
    ):
        await session.send_line("The guild ledger refuses to record your dues payment.")
        return

    _refresh_guild_state(session, server)
    due_str = new_due_date.strftime("%Y-%m-%d")
    await session.send_line(
        npc_speech(npc.display_name, f'says, "Your dues are recorded through {due_str}."')
    )
    await session.send_line(colorize(f"  You pay {amount} silver in guild dues.", TextPresets.ITEM_NAME))


async def _cmd_checkin(session, server):
    if not getattr(server, "db", None):
        await session.send_line("The guild system is unavailable right now.")
        return

    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    authority, npc = _get_local_authority(session, server, membership["guild_id"])
    if not npc:
        await session.send_line("You must be with a local guild authority to check in.")
        return

    monthly_dues = int(membership.get("monthly_dues") or 0)
    dues_paid_through = _as_dt(membership.get("dues_paid_through"))
    if monthly_dues > 0 and (not dues_paid_through or dues_paid_through < _utcnow()):
        await session.send_line(
            npc_speech(npc.display_name, 'says, "Your dues are not current.  Pay them before checking in."')
        )
        return

    checkin_days = 30 if int(membership.get("is_guildmaster", 0) or 0) else _CHECKIN_DAYS
    next_due = _utcnow() + timedelta(days=checkin_days)
    note = f"Checked in at room {session.current_room.id}."
    if not server.db.checkin_guild_member(
        session.character_id,
        membership["guild_id"],
        next_due,
        actor_template_id=getattr(npc, "template_id", None),
        notes=note,
    ):
        await session.send_line("The guild ledger refuses to record your check-in.")
        return

    _refresh_guild_state(session, server)
    if membership["guild_id"] == "rogue" and getattr(server, "guild", None):
        await server.guild.record_event(session, "guild_checkin_rogue")
    due_str = next_due.strftime("%Y-%m-%d")
    await session.send_line(
        npc_speech(npc.display_name, f'says, "You are checked in.  Return again before {due_str}."')
    )


async def _cmd_resign(session, server):
    if not getattr(server, "db", None):
        await session.send_line("The guild system is unavailable right now.")
        return

    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    guild_name = membership.get("guild_name", "guild")
    guild_id = membership["guild_id"]
    authority, npc = _get_local_authority(session, server, guild_id)
    note = f"Resigned at room {session.current_room.id if session.current_room else 0}."
    if not server.db.resign_guild_member(
        session.character_id,
        guild_id,
        actor_template_id=getattr(npc, "template_id", None) if npc else None,
        notes=note,
    ):
        await session.send_line("The guild ledger refuses to record your resignation.")
        return

    _refresh_guild_state(session, server)
    if npc:
        await session.send_line(
            npc_speech(npc.display_name, f'says, "Very well.  Your resignation from the {guild_name} is recorded."')
        )
    else:
        await session.send_line(f"Your resignation from the {guild_name} is recorded.")


def _active_task_line(task):
    if not task:
        return "You do not currently have an active guild task."
    progress = int(task.get("progress_count") or 0)
    target = int(task.get("target_count") or 1)
    skill = task.get("skill_name", "guild skill")
    text = task.get("task_text") or task.get("task_type") or "Guild task"
    if task.get("status") == "ready":
        return f"{skill}: {text}  [{progress}/{target}]  Ready to turn in with GLD COMPLETE."
    return f"{skill}: {text}  [{progress}/{target}]"


def _active_quest_line(quest):
    if not quest:
        return "You do not currently have an active rogue guild quest."
    progress = int(quest.get("progress_count") or 0)
    target = int(quest.get("target_count") or 1)
    title = quest.get("title", "Rogue Guild quest")
    objective = quest.get("objective") or quest.get("description") or title
    status = (quest.get("status") or "").lower()
    suffix = "  [Complete]" if status == "complete" else ""
    return f"Quest - {title}: {objective}  [{progress}/{target}]{suffix}"


def _active_general_quest_line(quest):
    if not quest:
        return "You do not currently have an active quest."
    progress = int(quest.get("progress_count") or 0)
    target = int(quest.get("target_count") or 1)
    title = quest.get("title", "Quest")
    objective = quest.get("objective") or quest.get("description") or title
    status = (quest.get("status") or "").lower()
    suffix = "  [Complete]" if status == "complete" else ""
    return f"{title}: {objective}  [{progress}/{target}]{suffix}"


def _find_local_generic_quest_npc(session, server, quest):
    if not getattr(server, "guild", None):
        return None
    return server.guild._find_local_quest_npc(session, quest, phase="start")


async def cmd_questslog(session, cmd, args, server):
    if not getattr(server, "guild", None):
        await session.send_line("The quest ledger is unavailable right now.")
        return
    if not getattr(session, "character_id", None):
        await session.send_line("The quest ledger cannot identify you right now.")
        return

    journal = server.guild.get_general_quest_journal(session.character_id)
    if not journal:
        await session.send_line("No general quests are currently configured.")
        return

    await session.send_line(colorize("Quest journal:", TextPresets.SYSTEM))
    for row in journal:
        status = (row.get("status") or "available").lower()
        label = status.capitalize()
        if status == "active":
            await session.send_line(f"  [{label}] {_active_general_quest_line(row)}")
            if row.get("hint"):
                await session.send_line(f"      Hint: {row.get('hint')}")
        else:
            await session.send_line(f"  [{label}] {row.get('title', 'Quest')} ({row.get('key_name', 'quest')}) - {row.get('description', '')}")


async def cmd_questlog(session, cmd, args, server):
    if not getattr(server, "guild", None):
        await session.send_line("The quest ledger is unavailable right now.")
        return
    if not getattr(session, "character_id", None):
        await session.send_line("The quest ledger cannot identify you right now.")
        return

    raw = (args or "").strip()
    parts = raw.split(None, 2) if raw else []
    subcmd = parts[0].lower() if parts else "status"
    remainder = raw[len(parts[0]):].strip() if parts else ""

    active = server.guild.get_active_quests(session.character_id, general_only=True)
    if subcmd in ("", "status"):
        if not active:
            await session.send_line("You do not currently have an active general quest.")
            return
        for row in active:
            await session.send_line(_active_general_quest_line(row))
            if row.get("hint"):
                await session.send_line(f"Hint: {row.get('hint')}")
        return

    if subcmd == "hint":
        if not active:
            await session.send_line("You do not currently have an active general quest.")
            return
        for row in active:
            await session.send_line(f"{row.get('title', 'Quest')}: {row.get('hint') or 'This quest does not currently offer an additional hint.'}")
        return

    if subcmd == "start":
        quest_key = remainder[len("start"):].strip() if remainder.lower().startswith("start") else remainder.strip()
        if not quest_key:
            await session.send_line("Use QUEST START <quest key>.")
            return

        quest_rows = server.guild.get_quest_journal(session.character_id, quest_key=quest_key)
        quest = quest_rows[0] if quest_rows else None
        if quest and not server.guild._is_general_quest(quest):
            await session.send_line("That quest belongs to a guild-specific track.  Use the appropriate guild quest command for it.")
            return
        actor_npc = _find_local_generic_quest_npc(session, server, quest) if quest else None
        ok, error, started = server.guild.start_quest(session, quest_key, actor_npc=actor_npc)
        if not ok:
            await session.send_line(error)
            return
        if actor_npc:
            await session.send_line(
                npc_speech(
                    actor_npc.display_name,
                    f'says, "Very well.  {started.get("title", "That work")} is yours now."'
                )
            )
        prepared, prep_error = await server.guild.prepare_started_quest(session, started, actor_npc=actor_npc)
        if not prepared:
            await session.send_line(prep_error or "That quest could not be prepared correctly.")
            return
        started_rows = server.guild.get_quest_journal(session.character_id, quest_key=quest_key)
        if started_rows:
            started = started_rows[0]
        await session.send_line(_active_general_quest_line(started))
        if started.get("hint"):
            await session.send_line(f"Hint: {started.get('hint')}")
        return

    await session.send_line("Use QUEST for status, QUEST HINT, QUEST START <quest key>, or QUESTS for the journal.")


async def cmd_answer(session, cmd, args, server):
    if not getattr(server, "guild", None):
        await session.send_line("There is nothing here waiting for your answer.")
        return
    await server.guild.answer_quiz(session, (args or "").strip())


async def _cmd_skills(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    guild_id = membership["guild_id"]
    defs = server.db.get_guild_skill_definitions(guild_id) if getattr(server, "db", None) else []
    if not defs:
        await session.send_line("This guild does not have any configured skill tracks yet.")
        return

    await session.send_line(colorize(f"{membership.get('guild_name', 'Guild')} skills:", TextPresets.SYSTEM))
    skill_rows = getattr(session, "guild_skills", {}) or {}
    active_skill = membership.get("active_skill_name")
    for row in defs:
        skill = row["skill_name"]
        current = skill_rows.get(skill, {})
        points = int(current.get("training_points", 0) or 0)
        ranks = int(current.get("ranks", 0) or 0)
        ppr = max(1, int(row.get("points_per_rank") or 100))
        next_need = ppr - (points % ppr) if ranks < int(row.get("max_rank") or 63) else 0
        focus_tag = "  [focus]" if active_skill == skill else ""
        practice_tag = "  [hall drill]" if int(row.get("practice_only") or 0) else ""
        await session.send_line(
            f"  {row.get('display_name', skill)}: rank {ranks}, {points} points"
            + (f", {next_need} to next rank" if next_need > 0 else ", mastered")
            + focus_tag + practice_tag
        )
    await session.send_line(_guild_cap_line(membership, session))


async def _cmd_task(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    current_task = None
    tasks = getattr(session, "guild_tasks", []) or []
    if tasks:
        current_task = tasks[0]
    if current_task and not args.strip():
        await session.send_line(_active_task_line(current_task))
        return
    if current_task and args.strip():
        await session.send_line("Finish or abandon your current guild task before requesting another.")
        return

    authority, npc = _get_local_authority(session, server, membership["guild_id"])
    if not npc:
        await session.send_line("You must be with a local guild authority to receive a new guild task.")
        return

    skill_name = None
    if args.strip():
        skill_name = server.guild.normalize_skill_name(membership["guild_id"], args.strip()) if getattr(server, "guild", None) else None
        if not skill_name:
            await session.send_line("That is not a recognized guild skill.  Use GLD SKILLS to review your tracks.")
            return
    else:
        defs = server.db.get_guild_skill_definitions(membership["guild_id"]) if getattr(server, "db", None) else []
        if not defs:
            await session.send_line("This guild does not have any configured tasks yet.")
            return
        skill_rows = getattr(session, "guild_skills", {}) or {}
        skill_name = min(
            defs,
            key=lambda row: (
                int((skill_rows.get(row["skill_name"], {}) or {}).get("ranks", 0) or 0),
                int(row.get("skill_order") or 0),
            ),
        )["skill_name"]

    ok, error, task = server.guild.assign_task(session, membership["guild_id"], skill_name)
    if not ok:
        await session.send_line(error)
        if task:
            await session.send_line(_active_task_line(task))
        return

    _refresh_guild_state(session, server)
    await session.send_line(
        npc_speech(npc.display_name, f'says, "Very well.  Here is your next {task.get("skill_name", "guild")} assignment."')
    )
    await session.send_line(_active_task_line(task))


async def _cmd_practice(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    authority, npc = _get_local_authority(session, server, membership["guild_id"])
    if not npc:
        await session.send_line("You must be with a local guild authority to work a hall-practice task.")
        return

    ok, error, _task = await server.guild.practice_active_task(session)
    if not ok:
        await session.send_line(error)
        return
    _refresh_guild_state(session, server)


async def _cmd_complete(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return

    authority, npc = _get_local_authority(session, server, membership["guild_id"])
    if not npc:
        await session.send_line("You must be with a local guild authority to turn in guild tasks.")
        return

    ok, error, summary = server.guild.complete_active_task(session) if getattr(server, "guild", None) else (False, "The guild system is unavailable right now.", None)
    if not ok:
        await session.send_line(error)
        return

    _refresh_guild_state(session, server)
    await session.send_line(
        npc_speech(
            npc.display_name,
            f'says, "Recorded.  You earn {summary["award_points"]} guild training points in {summary["skill_name"]}."'
        )
    )
    await session.send_line(
        f"Your {summary['skill_name']} skill is now rank {summary['skill_rank']}.  Total guild ranks: {summary['total_ranks']}."
    )
    await session.send_line(
        f"You now have {summary['vouchers']} task trading voucher{'s' if summary['vouchers'] != 1 else ''}."
    )
    if summary["new_rank"] > summary["old_rank"]:
        try:
            from server.core.commands.player.info import award_fame
            await award_fame(
                session, server, max(15, int(summary["new_rank"]) * 8), "guild_rank_up",
                detail_text=f"Advanced to guild rank {summary['new_rank']}.", quiet=True
            )
        except Exception:
            pass
        await session.send_line(
            colorize(
                f"  Guild promotion recorded: rank {summary['old_rank']} to rank {summary['new_rank']}.",
                TextPresets.COMBAT_HIT,
            )
        )


async def _cmd_quests(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership or membership.get("guild_id") != "rogue":
        await session.send_line("Rogue guild quests are only available to active members of the Rogue Guild.")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The rogue guild quest ledger is unavailable right now.")
        return

    journal = server.guild.get_quest_journal(session.character_id, "rogue")
    if not journal:
        await session.send_line("No rogue guild quests are currently configured.")
        return

    await session.send_line(colorize("Rogue guild quests:", TextPresets.SYSTEM))
    for row in journal:
        status = (row.get("status") or "available").lower()
        label = status.capitalize()
        if status == "active":
            await session.send_line(f"  [{label}] {_active_quest_line(row)}")
            if row.get("hint"):
                await session.send_line(f"      Hint: {row.get('hint')}")
        else:
            await session.send_line(f"  [{label}] {row.get('title', 'Quest')} - {row.get('description', '')}")


async def _cmd_quest(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership or membership.get("guild_id") != "rogue":
        await session.send_line("Rogue guild quests are only available to active members of the Rogue Guild.")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The rogue guild quest ledger is unavailable right now.")
        return

    subcmd = (args or "").strip().lower()
    active = server.guild.get_active_quest(session.character_id, "rogue")
    if not subcmd or subcmd == "status":
        if active:
            await session.send_line(_active_quest_line(active))
            if active.get("hint"):
                await session.send_line(f"Hint: {active.get('hint')}")
        else:
            await session.send_line("You do not currently have an active rogue guild quest.  Use GLD QUEST START.")
        return

    if subcmd == "hint":
        if not active:
            await session.send_line("You do not currently have an active rogue guild quest.")
            return
        await session.send_line(active.get("hint") or "This quest does not currently offer an additional hint.")
        return

    if subcmd == "start":
        authority, npc = _get_local_authority(session, server, "rogue")
        if not npc:
            await session.send_line("You must be with a local rogue guild authority to receive a guild quest.")
            return
        ok, error, quest = server.guild.start_next_quest(session, "rogue")
        if not ok:
            await session.send_line(error)
            return
        await session.send_line(
            npc_speech(
                npc.display_name,
                f'says, "Very well.  Your next quiet piece of work is {quest.get("title", "ready")}."'
            )
        )
        await session.send_line(_active_quest_line(quest))
        if quest.get("hint"):
            await session.send_line(f"Hint: {quest.get('hint')}")
        return

    await session.send_line("Use GLD QUEST, GLD QUEST START, or GLD QUEST HINT.")


async def _cmd_vouchers(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    await session.send_line(_voucher_line(membership))


async def _cmd_abandon(session, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The guild task system is unavailable right now.")
        return

    ok, error, task = server.guild.abandon_active_task(session)
    if not ok:
        await session.send_line(error)
        return
    _refresh_guild_state(session, server)
    await session.send_line(
        f"Your {task.get('skill_name', 'guild')} assignment has been abandoned."
    )


async def _cmd_swap(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The guild task system is unavailable right now.")
        return

    authority, npc = _get_local_authority(session, server, membership["guild_id"])
    if not npc:
        await session.send_line("You must be with a local guild authority to trade a guild task.")
        return

    skill_name = None
    if args.strip():
        skill_name = server.guild.normalize_skill_name(membership["guild_id"], args.strip())
        if not skill_name:
            await session.send_line("That is not a recognized guild skill.  Use GLD SKILLS to review your tracks.")
            return

    ok, error, task = server.guild.swap_active_task(session, membership["guild_id"], skill_name)
    if not ok:
        await session.send_line(error)
        return
    _refresh_guild_state(session, server)
    await session.send_line(
        npc_speech(
            npc.display_name,
            f'says, "Very well.  I have traded your assignment and recorded the voucher."'
        )
    )
    await session.send_line(_active_task_line(task))


async def _cmd_password(session, args, server):
    _refresh_guild_state(session, server)
    guild_engine = getattr(server, "guild", None)
    if not guild_engine:
        await session.send_line("The rogue access ledger is unavailable right now.")
        return

    membership = getattr(session, "guild_membership", None)
    guild_id = membership.get("guild_id") if membership else None
    if not guild_id:
        guild_id = "rogue"

    password_text = guild_engine.get_password_text(guild_id)
    if not password_text:
        await session.send_line("This guild does not currently have a password sequence configured.")
        return

    if not args.strip():
        access = guild_engine.get_access_row(session.character_id, guild_id) or {}
        if guild_id == "rogue" and not (membership or access.get("is_invited") or access.get("password_known")):
            await session.send_line("You do not currently have a rogue guild invitation or password on record.")
            return
        await session.send_line(f"The current sequence is {password_text}.")
        return

    if not membership or membership.get("guild_id") != guild_id or not int(membership.get("is_guildmaster", 0) or 0):
        await session.send_line("Only a guildmaster may reissue the rogue password to another member.")
        return

    target = _find_room_player(session, server, args.strip())
    if not target:
        await session.send_line("That person must be here with you before you can reissue the password.")
        return

    if not guild_engine.share_password(
        target.character_id,
        guild_id,
        actor_character_id=session.character_id,
    ):
        await session.send_line("The password ledger refuses to cooperate right now.")
        return

    await target.send_line(f"{session.character_name} quietly reviews the rogue entry sequence with you: {password_text}.")
    await session.send_line(f"You quietly review the sequence with {target.character_name}: {password_text}.")


async def _cmd_invite(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    if not int(membership.get("is_guildmaster", 0) or 0):
        await session.send_line("Only a guildmaster may issue invitations to other candidates.")
        return
    if not args.strip():
        await session.send_line("Invite whom?")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The guild invitation ledger is unavailable right now.")
        return

    target = _find_room_player(session, server, args.strip())
    if not target:
        await session.send_line("That person must be here with you before you can invite them.")
        return

    guild_id = membership["guild_id"]
    guild_def = server.db.get_guild_definition(guild_id) if getattr(server, "db", None) else None
    if not guild_def:
        await session.send_line("Your guild definition is unavailable right now.")
        return
    if int(getattr(target, "profession_id", 0) or 0) != int(guild_def.get("profession_id") or 0):
        await session.send_line("That person does not belong to your profession guild.")
        return
    if int(getattr(target, "level", 0) or 0) < int(guild_def.get("join_level") or 15):
        await session.send_line("That candidate has not yet reached guild joining level.")
        return
    if getattr(target, "guild_membership", None) and target.guild_membership.get("guild_id") == guild_id:
        await session.send_line("That person is already a member of your guild.")
        return

    password_known = guild_id == "rogue"
    if not server.guild.issue_invite(
        target.character_id,
        guild_id,
        actor_character_id=session.character_id,
        password_known=password_known,
        notes=f"Player-issued guild invitation from {session.character_name}.",
    ):
        await session.send_line("The invitation ledger refuses to record that right now.")
        return

    password_text = server.guild.get_password_text(guild_id)
    await session.send_line(f"You record an invitation for {target.character_name}.")
    if guild_id == "rogue" and password_text:
        await target.send_line(
            f"{session.character_name} quietly passes you a rogue invitation.  Your entry sequence is {password_text}."
        )
    else:
        await target.send_line(f"{session.character_name} records a standing invitation for you with the guild.")


async def _cmd_initiate(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    if not int(membership.get("is_guildmaster", 0) or 0):
        await session.send_line("Only a guildmaster may directly initiate a new member.")
        return
    if not args.strip():
        await session.send_line("Initiate whom?")
        return

    guild_id = membership["guild_id"]
    guild_def = server.db.get_guild_definition(guild_id) if getattr(server, "db", None) else None
    if not guild_def:
        await session.send_line("Your guild definition is unavailable right now.")
        return

    target = _find_room_player(session, server, args.strip())
    if not target:
        await session.send_line("That person must be here with you before you can initiate them.")
        return
    if int(getattr(target, "profession_id", 0) or 0) != int(guild_def.get("profession_id") or 0):
        await session.send_line("That person does not belong to your profession guild.")
        return
    if int(getattr(target, "level", 0) or 0) < int(guild_def.get("join_level") or 15):
        await session.send_line("That candidate has not yet reached guild joining level.")
        return
    if getattr(target, "guild_membership", None) and target.guild_membership.get("guild_id") == guild_id:
        await session.send_line("That person is already a member of your guild.")
        return

    initiation_fee = int(guild_def.get("initiation_fee") or 0)
    if int(getattr(target, "silver", 0) or 0) < initiation_fee:
        await session.send_line(f"{target.character_name} does not have the required {initiation_fee} silver.")
        return

    if initiation_fee > 0:
        target.silver -= initiation_fee
        server.db.save_character_resources(
            target.character_id,
            target.health_current, target.mana_current,
            target.spirit_current, target.stamina_current,
            target.silver,
        )

    if not server.db.join_guild_member(
        target.character_id,
        guild_id,
        actor_template_id=None,
        notes=f"Player guildmaster initiation by {session.character_name} in room {session.current_room.id}.",
    ):
        await session.send_line("The guild ledger refuses to record that initiation.")
        return

    if guild_id == "rogue" and getattr(server, "guild", None):
        server.guild.grant_member_access(target.character_id, guild_id)
        server.guild.share_password(target.character_id, guild_id, actor_character_id=session.character_id)

    _refresh_guild_state(target, server)
    await session.send_line(f"You welcome {target.character_name} into the {guild_def.get('name', 'guild')}.")
    await target.send_line(f"{session.character_name} initiates you into the {guild_def.get('name', 'guild')}.")
    if initiation_fee > 0:
        await target.send_line(f"You pay {initiation_fee} silver in initiation fees.")


async def _cmd_nominate(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    if not args.strip():
        await session.send_line("Nominate whom?")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The guild nomination ledger is unavailable right now.")
        return

    target_text = args.strip()
    if target_text.lower().endswith(" guildmaster"):
        target_text = target_text[:-12].strip()
    if target_text.lower().endswith(" master"):
        target_text = target_text[:-7].strip()

    target = _find_room_player(session, server, target_text)
    if not target:
        await session.send_line("That person must be here with you before you can nominate them.")
        return

    ok, error, count = server.guild.nominate_guildmaster(
        session.character_id,
        target.character_id,
        membership["guild_id"],
    )
    if not ok:
        await session.send_line(error)
        return

    await session.send_line(f"You nominate {target.character_name} for the office of guildmaster.")
    await target.send_line(f"{session.character_name} nominates you for the office of guildmaster.")
    await session.send_line(f"Active nominations on record: {count}.")


async def _cmd_promote(session, args, server):
    _refresh_guild_state(session, server)
    membership = getattr(session, "guild_membership", None)
    if not membership:
        await session.send_line("You are not currently a member of a profession guild.")
        return
    if not args.strip():
        await session.send_line("Promote whom, and in what way?")
        return
    if not getattr(server, "guild", None):
        await session.send_line("The guild promotion ledger is unavailable right now.")
        return

    raw = args.strip()
    lower = raw.lower()
    guild_id = membership["guild_id"]

    target_name = None
    skill_name = None
    guildmaster_mode = False

    if lower.startswith("guildmaster "):
        guildmaster_mode = True
        target_name = raw.split(None, 1)[1].strip()
    elif " guildmaster" in lower:
        guildmaster_mode = True
        target_name = raw[:lower.index(" guildmaster")].strip()
    elif " in " in lower:
        idx = lower.index(" in ")
        target_name = raw[:idx].strip()
        skill_name = raw[idx + 4:].strip()
    else:
        await session.send_line("Use GLD PROMOTE <person> IN <skill> or GLD PROMOTE GUILDMASTER <person>.")
        return

    target = _find_room_player(session, server, target_name)
    if not target:
        await session.send_line("That person must be here with you before you can promote them.")
        return

    if guildmaster_mode:
        ok, error, summary = server.guild.promote_guildmaster(session.character_id, target.character_id, guild_id)
        if not ok:
            await session.send_line(error)
            return
        _refresh_guild_state(target, server)
        try:
            from server.core.commands.player.info import award_fame
            await award_fame(
                target, server, 250, "guildmaster_promotion",
                detail_text=f"Named guildmaster of {guild_id}.", quiet=True
            )
        except Exception:
            pass
        await session.send_line(
            f"You complete the guildmaster promotion for {target.character_name}.  Total ranks recorded: {summary['total_ranks']}."
        )
        await target.send_line("You have been recognized as a guildmaster.")
        return

    normalized_skill = server.guild.normalize_skill_name(guild_id, skill_name)
    if not normalized_skill:
        await session.send_line("That is not a recognized guild skill.  Use GLD SKILLS to review the tracks.")
        return

    ok, error, summary = server.guild.promote_skill(
        session.character_id,
        target.character_id,
        guild_id,
        normalized_skill,
    )
    if not ok:
        await session.send_line(error)
        return
    _refresh_guild_state(target, server)
    try:
        from server.core.commands.player.info import award_fame
        await award_fame(
            target, server, max(10, int(summary.get('skill_rank') or 1) * 5), "guild_promotion",
            detail_text=f"Promoted in {summary.get('skill_name') or 'guild skill'}.", quiet=True
        )
    except Exception:
        pass
    await session.send_line(
        f"You promote {target.character_name} to rank {summary['skill_rank']} in {summary['skill_name']}."
    )
    await target.send_line(
        f"{session.character_name} promotes you to rank {summary['skill_rank']} in {summary['skill_name']}."
    )


def get_guild_npc_response(session, npc, topic, server):
    """Provide dynamic guild NPC responses before falling back to static dialogue."""
    guild_id = getattr(npc, "guild_id", None)
    if not guild_id:
        return None

    guild_def = server.db.get_guild_definition(guild_id) if getattr(server, "db", None) else None
    if not guild_def:
        return None

    membership = None
    if getattr(session, "guild_membership", None) and session.guild_membership.get("guild_id") == guild_id:
        membership = session.guild_membership

    topic_l = (topic or "guild").strip().lower()
    guild_name = guild_def.get("name", "guild")
    if guild_def.get("profession_id") != getattr(session, "profession_id", None):
        return f"I only handle {guild_name} business.  This is not your profession guild."
    if topic_l in ("join", "membership", "guild"):
        if membership:
            return f"You are already recorded in the {guild_name}.  Use GLD STATUS for the ledger summary."
        if guild_id == "rogue":
            if getattr(getattr(session, "current_room", None), "id", 0) == getattr(npc, "home_room_id", 0):
                return "If you made it inside, use GLD JOIN here and I can record your membership."
            return "If you are ready for rogue business, use GLD JOIN in the alley to receive your invitation and entry sequence."
        return f"If you are at least level {guild_def.get('join_level', 15)}, use GLD JOIN here and I can record your membership."
    if topic_l in ("invite", "password", "entry", "sequence"):
        if guild_id == "rogue":
            if membership:
                return "Your alley sequence remains: LEAN, then PULL, PULL, SLAP, RUB, RUB, PUSH, TURN."
            return "Rogue access begins with GLD JOIN in the alley.  Once invited, LEAN first and then use the entry sequence."
        return "This guild does not use a hidden entry sequence."
    if topic_l in ("dues", "pay", "silver"):
        return f"Monthly dues here are {int(guild_def.get('monthly_dues') or 0)} silver.  Use GLD PAY while standing here."
    if topic_l in ("checkin", "ledger", "register"):
        if membership:
            return _checkin_status_line(membership) + "  Use GLD CHECKIN once your dues are current."
        return "Once you are a member, GLD CHECKIN will record your next visit in the guild ledger."
    if topic_l in ("rank", "status"):
        if membership:
            return _guild_summary_line(membership) + "  Use GLD RANK or GLD STATUS for more."
        return f"The ledger shows no active {guild_name} membership for you."
    if topic_l in ("training", "skills"):
        if guild_def.get("has_skill_training"):
            return "Use GLD SKILLS to review your tracks, GLD TASK to receive work, GLD PRACTICE for hall drills, GLD COMPLETE to turn tasks in, and GLD QUEST START when you are ready for guided rogue work."
        return "This guild hall is social-only right now.  It does not currently offer guild skill training."
    if topic_l in ("task", "tasks", "practice"):
        if guild_def.get("has_skill_training"):
            return "Ask the ledger for work with GLD TASK.  Use GLD SWAP to trade a task, GLD ABANDON to drop one, and GLD COMPLETE to turn in finished work."
        return "This guild does not currently issue skill tasks."
    if topic_l in ("quest", "quests", "work", "assignment"):
        if guild_id == "rogue":
            return "For guided rogue training, use GLD QUEST START, GLD QUEST for status, and GLD QUEST HINT if you need the next nudge."
        return "This guild does not currently issue guided quest work."
    if topic_l in ("voucher", "vouchers", "swap", "trade"):
        return "Task trades use vouchers.  Check your count with GLD VOUCHERS and spend one with GLD SWAP."
    if topic_l in ("guildmaster", "nominate", "promote"):
        if guild_id == "rogue":
            return "Guildmaster candidates need 125 total guild ranks and one mastered skill.  Use GLD NOMINATE, then GLD PROMOTE GUILDMASTER once two nominations are on record."
        return "Guildmaster promotions require nominations and a formal promotion ritual."
    if topic_l in ("password", "sequence"):
        if guild_id == "rogue":
            return "Rogues may review the pass sequence with GLD PASSWORD.  Guildmasters may reissue it to another rogue."
        return "This guild does not use a hidden entry sequence."
    if topic_l in ("invite", "initiate"):
        return "Guildmasters can record invitations with GLD INVITE and bring candidates in directly with GLD INITIATE."
    if topic_l in ("resign", "leave"):
        return "If you truly wish to leave, use GLD RESIGN and the ledger will be updated."
    return None


async def maybe_handle_adventurer_guild_npc_response(session, npc, topic, server):
    """Allow Adventurer's Guild taskmasters to perform live registration/bounty actions."""
    engine = getattr(server, "guild", None)
    if not engine or not hasattr(engine, "handle_adventurer_guild_topic"):
        return False
    try:
        return await engine.handle_adventurer_guild_topic(session, npc, topic)
    except Exception:
        return False


def get_quest_npc_response(session, npc, topic, server):
    """Provide dynamic generic quest responses for quest-aware NPCs."""
    quest_engine = getattr(server, "guild", None)
    if not quest_engine or not getattr(session, "character_id", None):
        return None
    return quest_engine.get_npc_quest_response(session, npc, topic)


async def cmd_gld(session, cmd, args, server):
    """GLD - Guild status and membership verb."""
    option_text = (args or "").strip()
    if not option_text:
        await _show_status(session, server)
        return

    parts = option_text.split(None, 1)
    option = parts[0].lower()
    remainder = parts[1] if len(parts) > 1 else ""

    if option in ("menu", "help"):
        await _show_menu(session)
        return
    if option == "status":
        await _show_status(session, server)
        return
    if option == "join":
        await _cmd_join(session, server)
        return
    if option == "pay":
        await _cmd_pay(session, remainder, server)
        return
    if option == "checkin":
        await _cmd_checkin(session, server)
        return
    if option == "rank":
        await _cmd_rank(session, server)
        return
    if option == "skills":
        await _cmd_skills(session, server)
        return
    if option == "quests":
        await _cmd_quests(session, server)
        return
    if option == "quest":
        await _cmd_quest(session, remainder, server)
        return
    if option == "task":
        await _cmd_task(session, remainder, server)
        return
    if option == "practice":
        await _cmd_practice(session, server)
        return
    if option == "complete":
        await _cmd_complete(session, server)
        return
    if option == "vouchers":
        await _cmd_vouchers(session, server)
        return
    if option == "swap":
        await _cmd_swap(session, remainder, server)
        return
    if option == "abandon":
        await _cmd_abandon(session, server)
        return
    if option == "password":
        await _cmd_password(session, remainder, server)
        return
    if option == "invite":
        await _cmd_invite(session, remainder, server)
        return
    if option in ("init", "initiate"):
        await _cmd_initiate(session, remainder, server)
        return
    if option == "nominate":
        await _cmd_nominate(session, remainder, server)
        return
    if option == "promote":
        await _cmd_promote(session, remainder, server)
        return
    if option == "resign":
        await _cmd_resign(session, server)
        return

    await session.send_line(
        f"GLD supports: {', '.join(name.upper() for name in _SUPPORTED_OPTIONS)}.  Type GLD MENU for details."
    )
