"""
GemStone IV Information Commands
HEALTH, SKILLS, EXPERIENCE, INFO, WHO, WEALTH, HELP, TIME
All formatted to match GemStone IV output style.
"""

import logging
import datetime
from server.core.protocol.colors import (
    colorize, TextPresets, health_bar, player_name as fmt_player_name
)
from server.core.engine.encumbrance import (
    carry_capacity, carried_weight, encumbrance_pct,
    encumbrance_name, encumbrance_tier,
    encumbrance_as_ds_penalty, encumbrance_rt_penalty,
    format_weight_summary, format_weight_detail,
    TIER_NONE, TIER_SLIGHTLY, TIER_MODERATELY,
    TIER_HEAVILY, TIER_SEVERELY, TIER_OVERBURDENED,
)

log = logging.getLogger(__name__)

# Race ID to name mapping
RACES = {
    1: 'Human', 2: 'Elf', 3: 'Dark Elf', 4: 'Half-Elf',
    5: 'Dwarf', 6: 'Halfling', 7: 'Giantman', 8: 'Forest Gnome',
    9: 'Burghal Gnome', 10: 'Sylvankind', 11: 'Aelotoi',
    12: 'Erithian', 13: 'Half-Krolvin',
}

# Profession ID to name mapping
PROFESSIONS = {
    1: 'Warrior', 2: 'Rogue', 3: 'Wizard', 4: 'Cleric',
    5: 'Empath', 6: 'Sorcerer', 7: 'Ranger', 8: 'Bard',
    9: 'Monk', 10: 'Paladin', 11: 'Savant',
}

RACE_KEYS = {name.lower().replace("-", "").replace(" ", ""): rid for rid, name in RACES.items()}
PROFESSION_KEYS = {name.lower().replace("-", "").replace(" ", ""): pid for pid, name in PROFESSIONS.items()}

RACE_ABBREVS = {
    1: "Human", 2: "Elf", 3: "D-Elf", 4: "H-Elf",
    5: "Dwarf", 6: "Halfl", 7: "Giant", 8: "FGnom",
    9: "BGnom", 10: "Sylva", 11: "Aelot", 12: "Erith", 13: "HKrol",
}

PROFESSION_ABBREVS = {
    1: "War", 2: "Rog", 3: "Wiz", 4: "Cle",
    5: "Emp", 6: "Sor", 7: "Ran", 8: "Bar",
    9: "Mon", 10: "Pal", 11: "Sav",
}

FAME_PAGE_SIZE = 25
FAME_VISIBLE_CAP = 1000


def _stat_bonus(value):
    """GemStone IV stat bonus calculation: (stat - 50) / 2."""
    return (value - 50) // 2


async def award_fame(session, server, amount: int, source_key: str, detail_text: str | None = None, *, quiet: bool = True):
    """Add fame to a character and optionally notify them."""
    amount = int(amount or 0)
    if amount <= 0 or not getattr(server, "db", None) or not getattr(session, "character_id", None):
        return 0
    new_total = server.db.add_character_fame(session.character_id, amount, source_key, detail_text)
    if new_total is None:
        return 0
    session.fame = int(new_total)
    if not quiet:
        await session.send_line(colorize(f"  Fame: +{amount} ({session.fame:,} total)", TextPresets.SYSTEM))
    return amount


def _normalize_scope_token(text: str):
    token = str(text or "all").strip().lower()
    compact = token.replace("-", "").replace(" ", "")
    if token in ("all", "overall"):
        return "all", "All Fame"
    if compact in RACE_KEYS:
        race_id = RACE_KEYS[compact]
        return f"race:{race_id}", RACES.get(race_id, "Race")
    if compact in PROFESSION_KEYS:
        prof_id = PROFESSION_KEYS[compact]
        return f"profession:{prof_id}", PROFESSIONS.get(prof_id, "Profession")
    return None, None


def _gender_abbrev(value) -> str:
    token = str(value or "").strip().lower()
    if token.startswith("f"):
        return "F"
    if token.startswith("m"):
        return "M"
    return "?"


async def cmd_fame(session, cmd, args, server):
    """FAME - Show your fame, another character's fame, or fame lists."""
    if not getattr(server, "db", None):
        await session.send_line("The fame ledger is unavailable right now.")
        return

    raw = (args or "").strip()
    if not raw or raw.lower() in ("me", "self"):
        total = int(getattr(session, "fame", 0) or 0)
        list_state = "ON" if getattr(session, "fame_list_opt_in", False) else "OFF"
        await session.send_line(f"You currently have {colorize(f'{total:,}', TextPresets.EXPERIENCE)} fame.")
        await session.send_line(f"Your fame list setting is {list_state}.")
        return

    parts = raw.split()
    if parts[0].lower() == "stats":
        total = int(getattr(session, "fame", 0) or 0)
        list_state = "ON" if getattr(session, "fame_list_opt_in", False) else "OFF"
        stats = server.db.get_fame_stats(getattr(session, "character_id", None)) or {}
        await session.send_line(colorize("Fame statistics:", TextPresets.SYSTEM))
        await session.send_line(f"  Your fame: {total:,}")
        await session.send_line(f"  Fame list: {list_state}")
        await session.send_line(
            f"  Public entries: {int(stats.get('total_opted_in') or 0):,} "
            f"({int(stats.get('visible_count') or 0):,} visible / {int(stats.get('visible_cap') or FAME_VISIBLE_CAP):,} cap)"
        )
        top_fame = int(stats.get("top_fame") or 0)
        cutoff_fame = int(stats.get("cutoff_fame") or 0)
        if top_fame > 0:
            await session.send_line(f"  Highest visible fame: {top_fame:,}")
        if int(stats.get("visible_count") or 0) >= FAME_VISIBLE_CAP:
            await session.send_line(f"  Fame needed to appear: {cutoff_fame:,}")
        else:
            await session.send_line("  Fame needed to appear: none (list not full)")

        if stats.get("character_visible"):
            await session.send_line(f"  Overall rank: {int(stats.get('overall_rank') or 0):,}")
            if stats.get("race_rank"):
                await session.send_line(f"  Race rank: {int(stats.get('race_rank') or 0):,}")
            if stats.get("profession_rank"):
                await session.send_line(f"  Profession rank: {int(stats.get('profession_rank') or 0):,}")
        elif getattr(session, "fame_list_opt_in", False):
            await session.send_line("  You are not currently on the visible fame list.")
        else:
            await session.send_line("  You are not currently opted into the fame list.")
        return

    scope, label = _normalize_scope_token(parts[0])
    if scope:
        rank = 1
        if len(parts) > 1:
            try:
                rank = max(1, int(parts[1]))
            except Exception:
                rank = 1
        rows = server.db.get_fame_leaderboard(scope, rank=rank, limit=FAME_PAGE_SIZE) or []
        if not rows:
            await session.send_line(f"No fame list entries are available for {label}.")
            return
        await session.send_line(colorize(f"{label} Fame List", TextPresets.SYSTEM))
        await session.send_line(" Rank|     Name      |    Fame     |Lvl|G| Race|Prof")
        await session.send_line(" ---------------------------------------------------")
        idx = rank
        for row in rows:
            await session.send_line(
                f"{str(idx).rjust(5)} "
                f"{str(row.get('name') or '')[:16].ljust(16)} "
                f"{format(int(row.get('fame') or 0), ',').rjust(12)} "
                f"{str(int(row.get('level') or 0)).rjust(3)} "
                f"{_gender_abbrev(row.get('gender')).rjust(1)} "
                f"{RACE_ABBREVS.get(int(row.get('race_id') or 0), 'Unk').rjust(5)} "
                f"{PROFESSION_ABBREVS.get(int(row.get('profession_id') or 0), 'Unk').rjust(4)}"
            )
            idx += 1
        return

    target = server.db.get_character_by_name_basic(raw)
    if not target:
        await session.send_line("No one by that name is known to the fame ledger.")
        return
    await session.send_line(
        f"{target.get('name')} currently has {colorize(format(int(target.get('fame') or 0), ','), TextPresets.EXPERIENCE)} fame."
    )


async def cmd_set(session, cmd, args, server):
    """SET FAME ON|OFF - Toggle fame list participation."""
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        await session.send_line("Your settings ledger is unavailable right now.")
        return
    raw = (args or "").strip().lower()
    if not raw.startswith("fame"):
        await session.send_line("Usage: SET FAME ON or SET FAME OFF")
        return
    parts = raw.split()
    if len(parts) < 2 or parts[1] not in ("on", "off"):
        await session.send_line("Usage: SET FAME ON or SET FAME OFF")
        return
    session.fame_list_opt_in = (parts[1] == "on")
    ok = server.db.save_character_fame(session.character_id, int(getattr(session, "fame", 0) or 0), session.fame_list_opt_in)
    if not ok:
        await session.send_line("Your fame setting could not be updated.")
        return
    await session.send_line(f"Your fame list participation is now {'ON' if session.fame_list_opt_in else 'OFF'}.")


# =========================================================
# HEALTH
# =========================================================

async def cmd_health(session, cmd, args, server):
    """HEALTH - Show current health, mana, spirit, stamina."""
    await session.send_line('')
    await session.send_line(colorize('  ' + (session.character_name or 'Unknown'), TextPresets.SYSTEM))
    await session.send_line('')

    # Health
    h_cur = session.health_current
    h_max = session.health_max
    await session.send_line('  Maximum Health Points: ' + str(h_max) + '     Remaining: ' + colorize(str(h_cur), TextPresets.HEALTH_FULL if h_cur > h_max // 3 else TextPresets.WARNING))

    # Recovery rate — x4 multiplier matches game_loop._regen_tick
    con_bonus = _stat_bonus(session.stat_constitution)
    recovery = max(1, con_bonus // 2 + 1) * 4
    await session.send_line('  Health Recovery: ' + str(recovery) + ' points per round')
    await session.send_line('')

    # Spirit
    await session.send_line('  Maximum Spirit Points: ' + str(session.spirit_max) + '     Remaining: ' + colorize(str(session.spirit_current), TextPresets.EXPERIENCE))
    await session.send_line('')

    # Mana
    if session.mana_max > 0:
        await session.send_line('  Maximum Mana Points: ' + str(session.mana_max) + '      Remaining: ' + colorize(str(session.mana_current), TextPresets.EXPERIENCE))
        await session.send_line('')

    # Stamina
    sta_recovery = max(1, _stat_bonus(session.stat_constitution) + 2)
    await session.send_line('  Maximum Stamina Points: ' + str(session.stamina_max) + '    Remaining: ' + colorize(str(session.stamina_current), TextPresets.EXPERIENCE) + '  Recovery: ' + str(sta_recovery) + ' points per round')
    await session.send_line('')

    # Wounds - real injuries from combat
    injuries = getattr(session, 'injuries', {})
    if injuries:
        await session.send_line('  Wounds:')
        severity_names = {1: 'minor', 2: 'moderate', 3: 'serious', 4: 'severe', 5: 'critical'}
        for location, severity in sorted(injuries.items()):
            sev_name = severity_names.get(severity, 'serious')
            color = TextPresets.WARNING if severity >= 3 else TextPresets.SYSTEM
            await session.send_line(colorize(
                f'    {location.replace("_", " ").capitalize()}: {sev_name} wound',
                color
            ))
    else:
        await session.send_line('  Wounds: None')
    await session.send_line('  Scars: None')
    await session.send_line('')


# =========================================================
# SKILLS
# =========================================================

async def cmd_skills(session, cmd, args, server):
    """SKILLS - Show trained skills and remaining training points."""
    from server.core.commands.player.training import SKILL_NAMES, SKILL_CATEGORIES

    await session.send_line('')
    await session.send_line(colorize(
        '  ' + (session.character_name or 'Unknown') + ' (Level ' + str(session.level) + ')',
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        '  PTPs: ' + str(session.physical_tp) + '   MTPs: ' + str(session.mental_tp),
        TextPresets.SYSTEM
    ))
    await session.send_line('')
    await session.send_line('  ' + colorize('{:<30} {:>5}  {:>5}'.format('Skill Name', 'Ranks', 'Bonus'), TextPresets.SYSTEM))
    await session.send_line('  ' + '-' * 42)

    skills = session.skills or {}
    any_trained = False

    for category, skill_ids in SKILL_CATEGORIES.items():
        cat_lines = []
        for sid in skill_ids:
            data = skills.get(sid, {})
            if isinstance(data, dict):
                ranks = int(data.get('ranks', 0))
                bonus = int(data.get('bonus', 0))
            else:
                ranks, bonus = 0, 0
            if ranks > 0:
                name = SKILL_NAMES.get(sid, str(sid))
                cat_lines.append('  {:<30} {:>5}  {:>5}'.format(name, ranks, bonus))
                any_trained = True

        if cat_lines:
            await session.send_line(colorize('  -- ' + category + ' --', TextPresets.WARNING))
            for line in cat_lines:
                await session.send_line(line)

    if not any_trained:
        await session.send_line('  You have not yet trained in any skills.')
        await session.send_line('  Use TRAIN LIST to see available skills and costs.')

    await session.send_line('')
    await session.send_line(colorize(
        '  Training Points: ' + str(session.physical_tp) + ' physical, ' + str(session.mental_tp) + ' mental',
        TextPresets.SYSTEM
    ))
    await session.send_line('')


# =========================================================
# EXPERIENCE / EXP
# =========================================================

async def cmd_experience(session, cmd, args, server):
    """EXPERIENCE / EXP - Show experience, level, mind state, and absorption rate."""
    from server.core.engine.experience.experience_manager import (
        field_xp_capacity, get_mind_state, _get_absorb_rate, absorption_bar
    )

    capacity   = field_xp_capacity(session)
    field_exp  = getattr(session, 'field_experience', 0)
    total_exp  = getattr(session, 'experience', 0)
    fame_total = int(getattr(session, 'fame', 0) or 0)
    mind_state = get_mind_state(session)
    fill_pct   = field_exp / capacity if capacity > 0 else 0.0

    xp_mgr = getattr(server, 'experience', None)
    if xp_mgr and hasattr(xp_mgr, 'get_xp_progress'):
        _, xp_needed, pct_done = xp_mgr.get_xp_progress(session)
        next_level_xp = xp_mgr.xp_for_level(session.level + 1)
        total_xp = xp_mgr.xp_for_level(session.level)
        xp_remaining  = max(0, next_level_xp - total_exp)
    else:
        xp_needed    = 10000
        xp_remaining = max(0, xp_needed - total_exp)
        pct_done     = 0.0

    absorb_rate = _get_absorb_rate(session)

    if fill_pct < 0.25:
        mind_color = TextPresets.MIND_CLEAR
    elif fill_pct < 0.55:
        mind_color = TextPresets.MIND_FRESH
    elif fill_pct < 0.85:
        mind_color = TextPresets.MIND_MUDDLED
    else:
        mind_color = TextPresets.MIND_SATURATED

    room = getattr(session, 'current_room', None)
    room_type = ("supernode" if getattr(room, 'supernode', False)
                 else "node" if getattr(room, 'safe', False)
                 else "indoors" if getattr(room, 'indoor', False)
                 else "outdoors")

    await session.send_line('')
    await session.send_line(colorize(f'  {session.character_name or "Unknown"}', TextPresets.SYSTEM))
    await session.send_line('')
    await session.send_line(
        f'  Level: {colorize(str(session.level), TextPresets.EXPERIENCE)}'
        f'          Total Experience: {colorize(f"{total_exp:,}", TextPresets.EXPERIENCE)}'
    )
    await session.send_line(
        f'  Experience to next level: {colorize(f"{xp_remaining:,}", TextPresets.EXPERIENCE)}'
        f'  ({pct_done:.1f}% complete)'
    )
    await session.send_line(
        f'  Fame: {colorize(f"{fame_total:,}", TextPresets.EXPERIENCE)}'
    )
    await session.send_line('')
    await session.send_line(absorption_bar(session))
    await session.send_line(
        f'  Absorption: {colorize(str(absorb_rate) + " XP/pulse", TextPresets.SYSTEM)}'
        f'  ({room_type})'
    )
    await session.send_line('')
    await session.send_line(
        f'  PTPs: {colorize(str(session.physical_tp), TextPresets.SYSTEM)}'
        f'    MTPs: {colorize(str(session.mental_tp), TextPresets.SYSTEM)}'
    )
    await session.send_line('')


# =========================================================
# INFO
# =========================================================

async def cmd_info(session, cmd, args, server):
    """INFO - Full character info with stats."""
    race_name = RACES.get(session.race_id, 'Unknown')
    prof_name = PROFESSIONS.get(session.profession_id, 'Unknown')
    gender = (session.gender or 'Unknown').capitalize()

    await session.send_line('')
    await session.send_line(colorize('  Name: ' + (session.character_name or 'Unknown') + '   Race: ' + race_name + '   Profession: ' + prof_name, TextPresets.SYSTEM))
    await session.send_line('  Gender: ' + gender + '   Age: ' + str(getattr(session, 'age', '--')) + '   Level: ' + str(session.level))
    await session.send_line('  You have ' + colorize(str(session.silver), TextPresets.ITEM_NAME) + ' silver with you.')
    await session.send_line('')

    # Stats in two columns
    stats = [
        ('Strength (STR)', session.stat_strength, 'Dexterity (DEX)', session.stat_dexterity),
        ('Constitution (CON)', session.stat_constitution, 'Agility (AGI)', session.stat_agility),
        ('Discipline (DIS)', session.stat_discipline, 'Aura (AUR)', session.stat_aura),
        ('Logic (LOG)', session.stat_logic, 'Intuition (INT)', session.stat_intuition),
        ('Wisdom (WIS)', session.stat_wisdom, 'Influence (INF)', session.stat_influence),
    ]

    await session.send_line(colorize('  Statistics', TextPresets.SYSTEM))
    for left_name, left_val, right_name, right_val in stats:
        lb = _stat_bonus(left_val)
        rb = _stat_bonus(right_val)
        lb_str = '+' + str(lb) if lb >= 0 else str(lb)
        rb_str = '+' + str(rb) if rb >= 0 else str(rb)
        lc = TextPresets.EXPERIENCE if lb > 0 else (TextPresets.WARNING if lb < 0 else TextPresets.PROMPT)
        rc = TextPresets.EXPERIENCE if rb > 0 else (TextPresets.WARNING if rb < 0 else TextPresets.PROMPT)
        line = '    {:<20} {:>3}  ({})     {:<20} {:>3}  ({})'.format(
            left_name, left_val, colorize(lb_str, lc),
            right_name, right_val, colorize(rb_str, rc)
        )
        await session.send_line(line)

    await session.send_line('')
    await session.send_line('  Training Points: ' + str(session.physical_tp) + ' physical, ' + str(session.mental_tp) + ' mental')
    await session.send_line('')

    # Encumbrance summary
    enc_tier = encumbrance_tier(session)
    enc_line = format_weight_summary(session)
    if enc_tier == TIER_NONE:
        enc_color = TextPresets.EXPERIENCE
    elif enc_tier <= TIER_MODERATELY:
        enc_color = TextPresets.SYSTEM
    elif enc_tier <= TIER_HEAVILY:
        enc_color = TextPresets.WARNING
    else:
        enc_color = TextPresets.COMBAT_DAMAGE_TAKEN if hasattr(TextPresets, 'COMBAT_DAMAGE_TAKEN') else TextPresets.WARNING
    await session.send_line(colorize(enc_line, enc_color))
    if enc_tier >= TIER_SLIGHTLY:
        pen, rt = encumbrance_as_ds_penalty(session), encumbrance_rt_penalty(session)
        await session.send_line(colorize(
            f'  Encumbrance penalty: AS/DS {pen:+d}' + (f',  RT +{rt}' if rt else ''),
            TextPresets.WARNING
        ))
    await session.send_line('')


# =========================================================
# WHO
# =========================================================

async def cmd_who(session, cmd, args, server):
    """WHO - Show all connected players."""
    playing = server.sessions.playing()
    synthetic = list(getattr(getattr(server, "fake_players", None), "get_all", lambda: [])() or [])
    total_online = len(playing) + len(synthetic)

    await session.send_line('')
    await session.send_line(colorize(
        '  Online now: {} real, {} synthetic, {} total'.format(len(playing), len(synthetic), total_online),
        TextPresets.SYSTEM,
    ))
    await session.send_line('')
    await session.send_line('  {:<25} {:<8} {:<15} {}'.format('Name', 'Level', 'Profession', 'Location'))
    await session.send_line('  ' + '-' * 65)

    for s in playing:
        name = s.character_name or '???'
        level = str(s.level)
        prof = PROFESSIONS.get(s.profession_id, '???')
        loc = s.current_room.title if s.current_room else 'Unknown'
        await session.send_line('  {:<25} {:<8} {:<15} {}'.format(
            fmt_player_name(name), level, prof, loc
        ))

    for s in sorted(synthetic, key=lambda row: (str(getattr(row, "character_name", "") or "").lower(), int(getattr(row, "synthetic_id", 0) or 0))):
        name = '{} [Sim]'.format(getattr(s, "character_name", None) or '???')
        level = str(int(getattr(s, "level", 0) or 0))
        prof = PROFESSIONS.get(int(getattr(s, "profession_id", 0) or 0), getattr(s, "profession", '???') or '???')
        room = getattr(s, "current_room", None)
        loc = getattr(room, "title", None) or getattr(room, "name", None) or 'Unknown'
        await session.send_line('  {:<25} {:<8} {:<15} {}'.format(
            fmt_player_name(name), level, prof, loc
        ))

    await session.send_line('')


# =========================================================
# WEALTH
# =========================================================

async def cmd_wealth(session, cmd, args, server):
    """WEALTH - Show silver on hand and in bank."""
    await session.send_line('')
    await session.send_line('  You have ' + colorize(str(session.silver), TextPresets.ITEM_NAME) + ' silver with you.')
    await session.send_line('  You have ' + colorize(str(session.bank_silver), TextPresets.ITEM_NAME) + ' silver in the bank.')
    await session.send_line('')


# =========================================================
# TIME
# =========================================================

async def cmd_time(session, cmd, args, server):
    """TIME — Show current Elanthian date/time plus local weather if outdoors.

    GS4 canonical output:
      Today is Leyan, day 21 of the month Ivastaen in the year 5114.
      It is 20:46 by the elven time standard.
      It is currently late evening.

    Extended (private server addition — weather):
      The sky overhead is currently overcast.
    """
    from server.core.engine.time.elanthian_clock import ElanthianClock
    snap = ElanthianClock.now()

    await session.send_line("")
    await session.send_line(colorize(
        f"  Today is {snap['day_name']}, day {snap['day']} of the month "
        f"{snap['month_name']} in the year {snap['elanthian_year']}.",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        f"  It is {snap['time_24']} by the elven time standard.",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        f"  It is currently {snap['period']}.",
        TextPresets.SYSTEM
    ))

    # Holiday notice
    if snap.get("holiday"):
        await session.send_line(colorize(
            f"  Today is {snap['holiday']}.",
            TextPresets.EXPERIENCE
        ))

    # Weather — only shown outdoors
    room = session.current_room
    if room and not getattr(room, "indoor", False) and hasattr(server, "weather"):
        weather = server.weather.get_room_weather(room)
        state   = weather.get("state", "clear")
        if state and state != "still":
            label  = server.weather.get_weather_label(
                getattr(room, "zone_id", 0)
            )
            forced = weather.get("forced_by")
            if forced == "charm":
                weather_line = f"  The weather here has been unnaturally altered — it is {label}."
            else:
                weather_line = f"  The sky overhead is currently {label}."
            await session.send_line(colorize(weather_line, TextPresets.SYSTEM))

    await session.send_line("")


async def cmd_calendar(session, cmd, args, server):
    """CALENDAR [DAY|MONTH|TIME|HOLIDAY|CONVERT {YYYYMMDD}]

    GS4 canonical CALENDAR verb — full Elanthian calendar reference.
    """
    from server.core.engine.time.elanthian_clock import ElanthianClock

    sub = (args or "").strip().upper()

    if not sub or sub == "HELP":
        await session.send_line("")
        await session.send_line("  Usage:")
        await session.send_line("    CALENDAR DAY            - View Elanthian days with mundane equivalents.")
        await session.send_line("    CALENDAR MONTH          - View Elanthian months with mundane equivalents.")
        await session.send_line("    CALENDAR TIME           - View Elanthian times of day with mundane equivalents.")
        await session.send_line("    CALENDAR HOLIDAY        - View Elanthian holidays with mundane dates.")
        await session.send_line("    CALENDAR CONVERT {date} - Convert a mundane date to Elanthian.")
        await session.send_line("    Where {date} is in the format YYYYMMDD (e.g., 20260321 for March 21, 2026).")
        await session.send_line("")
        return

    if sub == "DAY":
        await session.send_line("")
        for line in ElanthianClock.calendar_day_table().splitlines():
            await session.send_line(f"  {line}")
        await session.send_line("")
        return

    if sub == "MONTH":
        await session.send_line("")
        for line in ElanthianClock.calendar_month_table().splitlines():
            await session.send_line(f"  {line}")
        await session.send_line("")
        return

    if sub == "TIME":
        await session.send_line("")
        for line in ElanthianClock.calendar_time_table().splitlines():
            await session.send_line(f"  {line}")
        await session.send_line("")
        return

    if sub == "HOLIDAY":
        await session.send_line("")
        for line in ElanthianClock.calendar_holiday_table().splitlines():
            await session.send_line(f"  {line}")
        await session.send_line("")
        return

    if sub.startswith("CONVERT"):
        parts    = sub.split()
        date_str = parts[1] if len(parts) > 1 else ""
        if not date_str or len(date_str) != 8 or not date_str.isdigit():
            await session.send_line(
                "  Usage: CALENDAR CONVERT {YYYYMMDD}  (e.g., CALENDAR CONVERT 20260321)"
            )
            return
        year  = int(date_str[0:4])
        month = int(date_str[4:6])
        day   = int(date_str[6:8])
        result = ElanthianClock.calendar_convert(year, month, day)
        await session.send_line(f"  {result}")
        return

    await session.send_line(
        f"  Unknown CALENDAR option '{args}'.  Type CALENDAR for usage."
    )


# =========================================================
# STATUS
# =========================================================

async def cmd_status(session, cmd, args, server):
    """STATUS - Show active status effects, injuries, and combat modifiers."""
    from server.core.engine.combat.status_effects import get_combat_mods

    await session.send_line('')
    await session.send_line(colorize('  Status: ' + (session.character_name or 'Unknown'), TextPresets.SYSTEM))
    await session.send_line('')

    # Active status effects
    status_rows = []
    sm = getattr(server, "status", None)
    if sm:
        for se in sm.get_all_active(session):
            defn = sm.get_def(se.effect_id) or {}
            if se.remaining < 0:
                remaining = "indefinite"
            else:
                remaining = f"{max(0, int(se.remaining))}s"
            status_rows.append({
                "name": defn.get("name", se.effect_id.replace("_", " ").title()),
                "remaining": remaining,
                "stacks": int(getattr(se, "stacks", 1) or 1),
                "description": defn.get("description", se.effect_id),
            })

    if getattr(session, "hidden", False) and not any(r["name"] == "Hidden" for r in status_rows):
        status_rows.append({
            "name": "Hidden",
            "remaining": "indefinite",
            "stacks": 1,
            "description": "Hidden from sight; revealed by movement or combat.",
        })
    if getattr(session, "sneaking", False) and not any(r["name"] == "Sneaking" for r in status_rows):
        status_rows.append({
            "name": "Sneaking",
            "remaining": "indefinite",
            "stacks": 1,
            "description": "Moving with stealth; each step rolls stealth instead of immediately breaking hiding.",
        })

    events = getattr(server, "events", None)
    if events and bool(getattr(events, "_lumnis_active", False)) and int(getattr(session, "lumnis_phase", 0) or 0) > 0:
        if not any(r["name"] == "Gift of Lumnis" for r in status_rows):
            phase = int(getattr(session, "lumnis_phase", 0) or 0)
            status_rows.append({
                "name": "Gift of Lumnis",
                "remaining": "indefinite",
                "stacks": 2 if phase == 1 else 1,
                "description": "Weekend blessing; bonus experience absorption is active.",
            })
    if events and bool(getattr(events, "_bonus_xp_active", False)):
        if not any(r["name"] == "Bonus Experience" for r in status_rows):
            status_rows.append({
                "name": "Bonus Experience",
                "remaining": "indefinite",
                "stacks": 1,
                "description": "Server-wide event bonus; creatures award additional experience.",
            })

    if status_rows:
        await session.send_line(colorize('  Active Effects:', TextPresets.SYSTEM))
        for row in status_rows:
            stacks = row.get('stacks', 1)
            stack_str = f' (x{stacks})' if stacks > 1 else ''
            await session.send_line(colorize(
                f'    {row["description"]}{stack_str} - {row["remaining"]}',
                TextPresets.WARNING
            ))
        await session.send_line('')
    else:
        await session.send_line('  Active Effects: None')
        await session.send_line('')

    # Injuries
    injuries = getattr(session, 'injuries', {})
    severity_names = {1: 'minor', 2: 'moderate', 3: 'serious', 4: 'severe', 5: 'critical'}
    if injuries:
        await session.send_line(colorize('  Injuries:', TextPresets.SYSTEM))
        for location, severity in sorted(injuries.items()):
            sev_name = severity_names.get(severity, 'serious')
            color = TextPresets.WARNING if severity >= 3 else TextPresets.SYSTEM
            await session.send_line(colorize(
                f'    {location.replace("_", " ").capitalize()}: {sev_name}',
                color
            ))
        await session.send_line('')
    else:
        await session.send_line('  Injuries: None')
        await session.send_line('')

    # Combat modifiers summary
    as_mod, ds_mod = get_combat_mods(session)
    inj_as = 0
    inj_ds = 0
    for loc, sev in injuries.items():
        if loc in ('right_arm', 'left_arm', 'right_hand', 'left_hand') and sev >= 3:
            inj_as -= sev * 3
        if sev >= 3:
            inj_ds -= sev * 2
    total_as = as_mod + inj_as
    total_ds = as_mod + inj_ds

    if total_as != 0 or total_ds != 0:
        await session.send_line(colorize('  Combat Penalties:', TextPresets.SYSTEM))
        if total_as != 0:
            await session.send_line(colorize(f'    Attack Strength:  {total_as:+d}', TextPresets.WARNING))
        if total_ds != 0:
            await session.send_line(colorize(f'    Defense Strength: {total_ds:+d}', TextPresets.WARNING))
        await session.send_line('')

    await session.send_line('')


# =========================================================
# HELP
# =========================================================

async def cmd_help(session, cmd, args, server):
    """HELP [topic] - Show available commands or help on a specific topic."""
    topic = (args or '').strip().lower()

    try:
        justice_mgr = getattr(server, "justice", None)
        if justice_mgr and topic and await justice_mgr.maybe_handle_help(session, topic):
            return
    except Exception as e:
        log.error("Justice HELP hook failed: %s", e)

    help_topics = {
        # ── Movement ──────────────────────────────────────────────────────
        'look':      'LOOK [target] — Look at your surroundings, a creature, player, or item.',
        'go':        'GO <exit> — Move through a named exit (e.g. GO BRIDGE).',
        'climb':     'CLIMB <target> — Climb an object or climbable exit.',

        # ── Communication ─────────────────────────────────────────────────
        'say':       "SAY <message> — Speak aloud to your room.  Alias: ' (apostrophe).",
        'whisper':   (
            'WHISPER <player> <message>           — IC whisper (room sees the act).\n'
            '  WHISPER IC <player> <message>      — Explicit IC whisper.\n'
            '  WHISPER OOC <player> <message>     — Out-of-character whisper.\n'
            '  WHISPER VISIBLE <player> <message> — Room sees you lean in, not what you say.\n'
            '  WHISPER GROUP <message>            — Whisper to your whole party (IC).\n'
            '  WHISPER OOC GROUP <message>        — OOC whisper to your whole party.'
        ),
        'yell':      (
            'YELL <message> — Yell loudly.  Three tiers of reach:\n'
            '  Same room     : Full message with your name.\n'
            '  1 room away   : "[Name] yells from the [direction], ...".\n'
            '  2 rooms away  : "You hear a distant yell...".'
        ),
        'shout':     'SHOUT <message> — Shout across your entire zone.',
        'tell':      'TELL <player> <message> — Private message to any online player (global range).',
        'sing':      'SING <lyrics> — Sing something aloud to your room.',
        'ask':       'ASK <player> ABOUT <topic> — Ask someone about a topic.',

        # ── ESP / Channels ─────────────────────────────────────────────────
        'esp':       (
            'ESP — Show your channel status and all ESP commands.\n'
            '  ESP TOGGLE              — Toggle ESP on or off.\n'
            '  ESP TUNE <channel>      — Tune to a channel.  Tuning twice sets it as default.\n'
            '  ESP UNTUNE <channel>    — Stop receiving a channel.\n'
            '  ESP WHO <channel> [FULL]— Show how many (or who) is tuned to a channel.\n'
            '  ESP IGNORE <player>     — Ignore a player on all channels.\n'
            '  ESP UNIGNORE <player>   — Stop ignoring a player.\n'
            '\n'
            '  Channels: General (IC), OOC, Help (OOC), Trade (OOC), Guild (IC, your profession).'
        ),
        'think':     (
            'THINK <message>              — Broadcast to your default ESP channel (General by default).\n'
            '  THINK TO <player> <message>  — Private thought to one player (global, any distance).\n'
            '  THINK ON <channel> <message> — Send to a specific channel this one time.'
        ),
        'chat':      "CHAT <message> — Shortcut for the OOC channel.  Same as THINK ON OOC <message>.",

        # ── Party ─────────────────────────────────────────────────────────
        'party':     (
            'PARTY START        — Form a new party.  Others in the room can type PARTY JOIN.\n'
            '  PARTY JOIN         — Join a party in your current room.\n'
            '  PARTY LEAVE        — Leave your current party.\n'
            '  PARTY END          — Disband the entire party.\n'
            '  PARTY / PARTY LIST — Show party roster and each member\'s location.\n'
            '\n'
            '  Movement: Any living party member in the same room follows automatically.\n'
            '  De-sync (death, different room) pauses follow; it resumes when everyone reunites.\n'
            '  XP: Every party member gets full XP on each kill, scaled to their own level.\n'
            '  Loot: Loot is individual — only the person looting gets the items.\n'
            '  Alias: PT'
        ),

        # ── Combat ────────────────────────────────────────────────────────
        'attack':    'ATTACK <target> — Basic melee attack.  Also: KILL, ATT.',
        'ambush':    'AMBUSH [target] [location] — Attack from hiding with an aimed strike.',
        'hide':      'HIDE — Attempt to conceal yourself in the shadows.',
        'sneak':     'SNEAK — Toggle sneaking mode.  Each step rolls stealth.',
        'stance':    'STANCE <type> — Change combat stance: offensive, advance, forward, neutral, guarded, defensive.',
        'aim':       'AIM <location> — Set a preferred aim location (head, neck, chest, etc.).',
        'feint':     'FEINT <target> — Reduce a creature\'s DS for one attack.',
        'search':    'SEARCH — Search a dead creature or room for hidden items.',
        'skin':      'SKIN <creature> — Skin a dead creature for materials.',

        # ── Inventory ─────────────────────────────────────────────────────
        'inventory': 'INVENTORY [FULL|HANDS] — Show your inventory.  Alias: INV.',
        'get':       'GET <item> [FROM <container>] — Pick up an item.  Alias: TAKE.',
        'drop':      'DROP <item> — Drop a held item on the ground.',
        'put':       'PUT <item> IN <container> — Put a held item into an open container.',
        'give':      'GIVE <item> TO <player> — Give a held item to another player.',
        'swap':      'SWAP — Swap items between left and right hands.',
        'wear':      'WEAR <item> — Wear or wield an item from your hands.  Alias: WIELD.',
        'remove':    'REMOVE <item> — Remove a worn item and hold it.',
        'stow':      'STOW [item] — Stow a held item into your first available container.',
        'open':      'OPEN <container> — Open a container.',
        'close':     'CLOSE <container> — Close a container.',
        'loot':      'LOOT — Search and auto-stow items from a dead creature.',
        'inspect':   'INSPECT <item> — Examine an item in detail.  Alias: INSP.',
        'mark':      'MARK <item> — Protect an item from bulk selling.  MARK REMOVE <item> to unmark.',
        'dye':       'DYE <item> <color> — Dye a worn item.  DYE HAIR <color>.  DYE COLORS for list.',

        # ── Information ───────────────────────────────────────────────────
        'health':    'HEALTH — Show current health, mana, spirit, and stamina.  Alias: HP.',
        'status':    'STATUS — Show active status effects, injuries, and combat modifiers.  Alias: STAT.',
        'info':      'INFO — Show your full character sheet.',
        'skills':    'SKILLS [BASE|FULL] — Show your trained skills.  Alias: SKILL.',
        'experience':'EXPERIENCE — Show XP, level progress, mind state, and fame.  Alias: EXP.',
        'fame':      'FAME — Show your fame, another character\'s fame, or the fame lists.  Use SET FAME ON|OFF for list participation.',
        'set':       'SET FAME ON|OFF — Control whether you appear on the fame lists.',
        'wealth':    'WEALTH — Show silver on hand and in bank.',
        'who':       'WHO — List all online players.',
        'time':      'TIME — Show the current in-game time and date.',
        'weight':    'WEIGHT — Show your carried weight and encumbrance tier.  Aliases: WT, ENCUMBRANCE.',
        'quest':     'QUEST — Show your active general quest status.  QUEST HINT reviews active hints.  QUEST START <quest key> begins a local quest when available.',
        'quests':    'QUESTS — Review your general quest journal.',
        'answer':    'ANSWER <response> — Reply to an active quiz-style lesson or quest prompt.',

        # ── Actions ───────────────────────────────────────────────────────
        'stand':     'STAND — Stand up.',
        'sit':       'SIT — Sit down.',
        'kneel':     'KNEEL — Kneel.',
        'lie':       'LIE — Lie down.',
        'rest':      'REST — Rest (recover faster).',
        'sleep':     'SLEEP — Sleep.',
        'tend':      'TEND — Tend to your wounds to slow bleeding.',
        'wounds':    'WOUNDS — Show your current injuries.  Aliases: WOUND, INJURIES, INJ.',
        'use':       'USE <item> — Use, eat, drink, or apply an item.  Aliases: EAT, DRINK, APPLY.',
        'emote':     'EMOTE <action> — Perform a custom free-form emote.  Alias: EM.',

        # ── Lockpicking ───────────────────────────────────────────────────
        'pick':      'PICK <lockbox> — Attempt to pick a lock (requires Picking Locks skill).',
        'disarm':    'DISARM <lockbox> — Attempt to disarm a trap.',
        'detect':    'DETECT <lockbox> — Check a box for traps before picking.',
        'submit':    'SUBMIT <box> — Submit a locked box to a locksmith queue.',
        'myjobs':    'MYJOBS — View your pending locksmith jobs.',

        # ── Shopping ──────────────────────────────────────────────────────
        'order':     'ORDER — Browse a shop\'s catalog.',
        'buy':       'BUY <#> — Purchase item number # from a shop.  Alias: PURCHASE.',
        'sell':      'SELL <item|container> — Sell a held item or bulk-sell a container\'s contents.',
        'appraise':  'APPRAISE <item> — Get the sell value of a held item.',

        # ── Banking ───────────────────────────────────────────────────────
        'deposit':   'DEPOSIT <amount> — Deposit silver at a bank.',
        'withdraw':  'WITHDRAW <amount> — Withdraw silver from a bank.',
        'check':     'CHECK — Check your bank balance.',

        # ── Training / Character ──────────────────────────────────────────
        'train':     'TRAIN — Open the skill training interface (at an inn).',
        'fixstats':  'FIXSTATS — Reassign base stats (requires a fixstats potion).',
        'weapon':    'WEAPON — View weapon technique options.',
        'customize': 'CUSTOMIZE <item> — Customize material/color of an item at a qualifying shop.',
    }

    if topic:
        if topic in help_topics:
            await session.send_line('')
            for line in help_topics[topic].split('\n'):
                await session.send_line('  ' + line)
            await session.send_line('')
        else:
            # Try partial match
            matches = [k for k in help_topics if k.startswith(topic)]
            if len(matches) == 1:
                await session.send_line('')
                for line in help_topics[matches[0]].split('\n'):
                    await session.send_line('  ' + line)
                await session.send_line('')
            elif matches:
                await session.send_line(
                    colorize(f"  Did you mean: {', '.join(sorted(matches))}?", TextPresets.SYSTEM)
                )
            else:
                await session.send_line(f"  No help available for '{topic}'.  Type HELP for a full list.")
        return

    # ── Full help listing ─────────────────────────────────────────────────
    await session.send_line('')
    await session.send_line(colorize('  ╔══════════════════════════════════════════════╗', TextPresets.SYSTEM))
    await session.send_line(colorize('  ║       GemStone IV Command Reference          ║', TextPresets.SYSTEM))
    await session.send_line(colorize('  ╚══════════════════════════════════════════════╝', TextPresets.SYSTEM))
    await session.send_line('')

    await session.send_line(colorize('  MOVEMENT', TextPresets.SYSTEM))
    await session.send_line('    N S E W NE NW SE SW  UP  DOWN  OUT  GO <exit>  CLIMB <target>  LOOK (L)')
    await session.send_line('')

    await session.send_line(colorize('  COMMUNICATION', TextPresets.SYSTEM))
    await session.send_line("    SAY (')    WHISPER [IC|OOC|VISIBLE] <player>    WHISPER GROUP")
    await session.send_line('    YELL       SHOUT       SING       TELL <player>       ASK')
    await session.send_line('')

    await session.send_line(colorize('  ESP / CHANNELS  (type HELP ESP for full details)', TextPresets.CHANNEL_GENERAL))
    await session.send_line(colorize('    Channels: General · OOC · Help · Trade · Guild', TextPresets.CHANNEL_GENERAL))
    await session.send_line(colorize('    ESP TUNE/UNTUNE/TOGGLE/WHO/IGNORE', TextPresets.CHANNEL_GENERAL))
    await session.send_line(colorize('    THINK <msg>   THINK TO <player>   THINK ON <channel>', TextPresets.CHANNEL_GENERAL))
    await session.send_line(colorize('    CHAT <msg>  — OOC shortcut', TextPresets.CHANNEL_OOC))
    await session.send_line('')

    await session.send_line(colorize('  PARTY  (type HELP PARTY for full details)', TextPresets.SYSTEM))
    await session.send_line('    PARTY START  PARTY JOIN  PARTY LEAVE  PARTY END  PARTY LIST')
    await session.send_line('    — Party members auto-follow movement.  XP shared on kills.')
    await session.send_line('')

    await session.send_line(colorize('  COMBAT', TextPresets.SYSTEM))
    await session.send_line('    ATTACK (ATT)   KILL   AMBUSH   FEINT   AIM <loc>')
    await session.send_line('    HIDE   SNEAK   STANCE <type>   SEARCH   SKIN')
    await session.send_line('')

    await session.send_line(colorize('  INVENTORY', TextPresets.SYSTEM))
    await session.send_line('    INVENTORY (INV)   GET (TAKE)   DROP   PUT   GIVE   SWAP')
    await session.send_line('    WEAR (WIELD)   REMOVE   STOW   OPEN   CLOSE   LOOT')
    await session.send_line('    INSPECT (INSP)   MARK   DYE')
    await session.send_line('')

    await session.send_line(colorize('  INFORMATION', TextPresets.SYSTEM))
    await session.send_line('    HEALTH (HP)   STATUS (STAT)   INFO   SKILLS   EXP   FAME   WEALTH')
    await session.send_line('    WHO   TIME   WEIGHT (WT)   WOUNDS (INJ)   QUEST   QUESTS')
    await session.send_line('')

    await session.send_line(colorize('  ACTIONS', TextPresets.SYSTEM))
    await session.send_line('    STAND  SIT  KNEEL  LIE  REST  SLEEP  TEND  USE  EMOTE (EM)')
    await session.send_line('')

    await session.send_line(colorize('  LOCKPICKING', TextPresets.SYSTEM))
    await session.send_line('    PICK   DISARM   DETECT   SUBMIT   MYJOBS')
    await session.send_line('')

    await session.send_line(colorize('  SHOPPING & BANKING', TextPresets.SYSTEM))
    await session.send_line('    ORDER   BUY   SELL   APPRAISE')
    await session.send_line('    DEPOSIT   WITHDRAW   CHECK')
    await session.send_line('')

    await session.send_line(colorize('  CHARACTER', TextPresets.SYSTEM))
    await session.send_line('    TRAIN   FIXSTATS   WEAPON   CUSTOMIZE')
    await session.send_line('')

    await session.send_line(colorize('  Type HELP <command> for details on any command.', TextPresets.SYSTEM))
    await session.send_line(colorize('  Example: HELP WHISPER   HELP ESP   HELP PARTY   HELP YELL', TextPresets.SYSTEM))
    await session.send_line('')


# =========================================================
# WEIGHT
# =========================================================

async def cmd_weight(session, cmd, args, server):
    """WEIGHT [DETAIL] - Show carried weight vs. capacity and encumbrance status.

    WEIGHT        — one-line summary
    WEIGHT DETAIL — full per-item breakdown
    """
    sub = (args or '').strip().lower()

    await session.send_line('')

    if sub in ('detail', 'full', 'list'):
        await session.send_line(colorize(
            '  Encumbrance — Carry Weight Detail', TextPresets.SYSTEM
        ))
        await session.send_line(colorize('  ' + '─' * 50, TextPresets.SYSTEM))
        for line in format_weight_detail(session):
            # Color the status line based on tier
            tier = encumbrance_tier(session)
            if 'OVERBURDENED' in line:
                await session.send_line(colorize(line, TextPresets.WARNING))
            elif 'encumbered' in line.lower() and tier >= TIER_MODERATELY:
                await session.send_line(colorize(line, TextPresets.WARNING))
            else:
                await session.send_line(line)
    else:
        # Single-line summary
        tier    = encumbrance_tier(session)
        summary = format_weight_summary(session)

        if tier == TIER_NONE:
            col = TextPresets.EXPERIENCE
        elif tier <= TIER_MODERATELY:
            col = TextPresets.SYSTEM
        else:
            col = TextPresets.WARNING

        await session.send_line(colorize(summary, col))

        # Show combat penalty when relevant
        if tier >= TIER_SLIGHTLY:
            pen = encumbrance_as_ds_penalty(session)
            rt  = encumbrance_rt_penalty(session)
            parts = [f'AS/DS {pen:+d}']
            if rt:
                parts.append(f'RT +{rt}')
            await session.send_line(colorize(
                '  Encumbrance penalty: ' + ', '.join(parts),
                TextPresets.WARNING
            ))

        # Tip for overburdened
        if tier == TIER_OVERBURDENED:
            await session.send_line(colorize(
                '  WARNING: You are overburdened! Drop items immediately.',
                TextPresets.WARNING
            ))

        await session.send_line(
            colorize('  (Type WEIGHT DETAIL for per-item breakdown.)', TextPresets.SYSTEM)
        )

    await session.send_line('')
