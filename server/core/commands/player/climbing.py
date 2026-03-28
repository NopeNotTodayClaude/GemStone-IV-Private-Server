"""
climbing.py  -  GemStone IV CLIMB verb with skill check system.

GS4 Canon:
  - CLIMB is a distinct verb, not an alias for GO
  - Uses an open d100 roll + climbing skill bonus + DEX bonus + modifiers
  - Must exceed a difficulty threshold set per exit (climb_difficulty in room Lua)
  - Factors: climbing ranks, DEX stat, encumbrance, armor hindrance, injuries
  - On success:  player moves, brief roundtime (1-3s)
  - On soft fail: slip, no movement, roundtime (3s), small damage possible
  - On hard fail: fall, take damage, knocked prone, longer roundtime (5s)
  - Climbing 50 ranks lets you climb anywhere per wiki ("50 ranks = climb anywhere")

Difficulty values (set in room Lua as climb_difficulty, default 30):
  10  = trivial (short ladder, low wall)
  20  = easy    (catacomb grate, standard ladder)
  30  = average (city wall)
  50  = hard    (cliff face, castle wall)
  75  = very hard (mountain)
  100 = extreme (requires 50+ ranks to have reasonable success)

Formula (matches GS4 standard maneuver roll):
  result = open_d100 + climbing_bonus + dex_bonus - encumbrance_penalty
           - armor_hindrance_penalty - injury_penalty
  success if result > difficulty (threshold = 100 means ~50% at 0 ranks)
"""

import random
import logging
from server.core.protocol.colors import colorize, TextPresets
from server.core.commands.player.movement import _move_player
from server.core.world.room import normalize_exit_key
from server.core.engine.encumbrance import encumbrance_pct, carry_capacity, carried_weight
from server.core.engine.magic_effects import apply_roundtime_effects, get_active_buff_totals

log = logging.getLogger(__name__)

# Skill IDs (from skills seed)
SKILL_CLIMBING       = 28
SKILL_SWIMMING       = 29
SKILL_PHYSICAL_FITNESS = 13

# Default difficulty if room doesn't specify
DEFAULT_DIFFICULTY = 20

# Difficulty per climb exit type (keyed to the object name after climb_)
CLIMB_DIFFICULTIES = {
    "grate":     20,
    "ladder":    20,
    "wall":      40,
    "cliff":     60,
    "rope":      30,
    "staircase": 10,
    "stair":     10,
    "rubble":    35,
    "tree":      40,
    "rocks":     45,
}

# Failure messages (soft fail)
SLIP_MESSAGES = [
    "You reach for a handhold but your grip slips!  You fail to make any progress.",
    "Your foot loses its purchase and you slide back down a short distance.",
    "You lose your footing and scramble to regain your balance.",
    "The surface is treacherous.  You fail to make headway and catch yourself.",
    "You slip and nearly fall, barely managing to hold on.",
]

# Fall messages (hard fail)
FALL_MESSAGES = [
    "You lose your grip entirely and fall!",
    "Your footing gives way and you tumble down!",
    "You slip and plummet downward!",
]

SWIM_DIFFICULTIES = {
    "water":   25,
    "bank":    20,
    "island":  35,
    "opening": 30,
    "out":     20,
    "up":      25,
    "down":    40,
    "north":   30,
    "south":   30,
    "east":    30,
    "west":    30,
}

SWIM_FAIL_MESSAGES = [
    "You strike out into the water but fail to make headway.",
    "You flounder and swallow a mouthful of water before regaining yourself.",
    "The current drags at you and forces you back.",
    "You kick hard, but the water resists your progress.",
]


def _open_d100():
    """
    GS4 open d100: base 1-100 with 5% chance to explode high (add another d100)
    and 5% chance to go negative (subtract another d100).
    """
    roll = random.randint(1, 100)
    if roll <= 5:
        # Potential negative roll
        roll -= random.randint(1, 100)
    elif roll >= 96:
        # Potential exploding roll
        roll += random.randint(1, 100)
    return roll


def _get_skill_bonus(ranks: int) -> int:
    """
    GS4 canonical skill bonus formula (gswiki.play.net/Skill):
      Ranks  1-10: +5 per rank  (max  50)
      Ranks 11-20: +4 per rank  (max  90)
      Ranks 21-30: +3 per rank  (max 120)
      Ranks 31-40: +2 per rank  (max 140)
      Ranks   41+: +1 per rank  (= rank + 100)
    """
    if ranks <= 0:  return 0
    if ranks <= 10: return ranks * 5
    if ranks <= 20: return 50 + (ranks - 10) * 4
    if ranks <= 30: return 90 + (ranks - 20) * 3
    if ranks <= 40: return 120 + (ranks - 30) * 2
    return ranks + 100


def _get_stat_bonus(stat_value: int) -> int:
    """Convert raw stat to bonus: (stat - 50) // 2, roughly."""
    return (stat_value - 50) // 2


def _get_encumbrance_penalty(session) -> int:
    """
    Climbing encumbrance penalty — delegates to the canonical encumbrance engine.
    Returns an integer penalty (0–100) proportional to % of carry capacity used.
    1 point of climbing penalty per 1% of capacity carried.
    """
    pct = encumbrance_pct(session)
    return min(100, int(pct))


def _get_armor_penalty(session) -> int:
    """
    Armor action penalty reduces climbing ability.
    Uses armor_asg (Armor Strength Group, int 1-20) — the canonical numeric
    armor field used throughout the codebase.  armor_group is a string label
    ('cloth', 'leather', etc.) and must not be used for numeric comparison.

    ASG thresholds (GS4 canon):
      1-4   = unencumbering (robes, leather)  -> 0 penalty
      5-9   = light metal / chain             -> 5 penalty
      10-15 = heavy chain / plate             -> 10 penalty
      16-20 = full plate / tower shield sets  -> 20 penalty
    """
    asg = 0
    for item in getattr(session, "inventory", []):
        if item.get("item_type") == "armor" and item.get("slot"):
            try:
                asg = max(asg, int(item.get("armor_asg") or 0))
            except (TypeError, ValueError):
                pass

    if asg <= 4:
        return 0
    elif asg <= 9:
        return 5
    elif asg <= 15:
        return 10
    else:
        return 20


def _get_difficulty(room, target: str) -> int:
    """Get the climb difficulty for this room/target."""
    # Check if room has a custom difficulty set in Lua data
    custom = getattr(room, "climb_difficulty", None)
    if custom:
        return int(custom)
    # Look up by target name
    return CLIMB_DIFFICULTIES.get(target.lower(), DEFAULT_DIFFICULTY)


def _get_swim_difficulty(target: str) -> int:
    return SWIM_DIFFICULTIES.get((target or "").lower(), 30)


async def cmd_climb(session, cmd, args, server):
    """
    CLIMB <target>  -  Attempt to climb something with a skill check.
    
    Success: move to the target room, apply minor roundtime.
    Soft fail: slip, stay, roundtime 3s, maybe minor damage.
    Hard fail: fall, take damage, knocked prone, roundtime 5s.
    """
    room = session.current_room
    if not room:
        await session.send_line("You can't do that right now.")
        return

    if session.position != "standing":
        await session.send_line("You need to stand up first.")
        return

    raw_target = (args or "").strip().lower()
    target = normalize_exit_key(raw_target)
    display_target = raw_target or target.replace("_", " ")
    if not target:
        # Show available climbs
        climbs = [k[6:].replace("_", " ") for k in room.exits if k.startswith("climb_")]
        if climbs:
            await session.send_line(f"Climb what?  Options here: {', '.join(climbs)}")
        else:
            await session.send_line("There's nothing obvious to climb here.")
        return

    # Find the exit
    exit_key = f"climb_{target}"
    target_room_id = room.exits.get(exit_key)

    # Also allow plain "climb ladder" if there's a go_ladder exit
    if target_room_id is None:
        target_room_id = room.exits.get(f"go_{target}")
    if target_room_id is None:
        target_room_id = room.exits.get(target)

    if target_room_id is None:
        await session.send_line(f"You don't see any '{display_target}' to climb here.")
        return

    target_room = server.world.get_room(target_room_id)
    if not target_room:
        await session.send_line("That exit leads nowhere... (room not loaded)")
        return

    # ── Build the skill check ────────────────────────────────────────────────
    skills = getattr(session, "skills", {}) or {}

    # Skills keyed by int skill_id in DB: {28: {"ranks": X, "bonus": Y}}
    climbing_data = skills.get(SKILL_CLIMBING, {})
    pf_data       = skills.get(SKILL_PHYSICAL_FITNESS, {})
    climbing_ranks = climbing_data.get("ranks", 0) if isinstance(climbing_data, dict) else 0
    pf_ranks       = pf_data.get("ranks", 0)       if isinstance(pf_data, dict) else 0

    dex_stat = getattr(session, "stat_dexterity", 50)
    agi_stat = getattr(session, "stat_agility", 50)

    climbing_bonus = _get_skill_bonus(climbing_ranks)
    pf_bonus = _get_skill_bonus(pf_ranks) // 4       # PF contributes ~25%
    dex_bonus = _get_stat_bonus(dex_stat)
    agi_bonus = _get_stat_bonus(agi_stat) // 2       # AGI contributes half

    encumb_pen = _get_encumbrance_penalty(session)
    armor_pen  = _get_armor_penalty(session)

    buffs = get_active_buff_totals(server, session)
    total_bonus = climbing_bonus + pf_bonus + dex_bonus + agi_bonus - encumb_pen - armor_pen
    if buffs.get("movement_bonus"):
        total_bonus += 10

    roll = _open_d100()
    result = roll + total_bonus
    difficulty = _get_difficulty(room, target)

    log.debug(
        "CLIMB %s: roll=%d bonus=%d (climb=%d pf=%d dex=%d agi=%d enc=-%d armor=-%d) "
        "result=%d difficulty=%d",
        display_target, roll, total_bonus, climbing_bonus, pf_bonus,
        dex_bonus, agi_bonus, encumb_pen, armor_pen, result, difficulty
    )

    # ── 50-rank guarantee ────────────────────────────────────────────────────
    # Per wiki: "Climbing 50 Ranks will let you climb anywhere"
    if climbing_ranks >= 50:
        result = max(result, difficulty + 1)

    # ── Evaluate result ──────────────────────────────────────────────────────
    margin = result - difficulty

    if margin > 0:
        # ── SUCCESS ──────────────────────────────────────────────────────────
        if margin >= 50:
            await session.send_line(colorize(
                f"You scale the {display_target} with practiced ease.",
                TextPresets.SYSTEM
            ))
            rt = 1
        elif margin >= 20:
            await session.send_line(f"You carefully climb the {display_target}.")
            rt = 2
        else:
            await session.send_line(f"You manage to climb the {display_target}, though it takes some effort.")
            rt = 3

        rt = apply_roundtime_effects(rt, server, session)
        session.set_roundtime(rt)
        await _move_player(session, room, target_room, f"up the {display_target}", server,
                           sneaking=session.hidden or getattr(session, "sneaking", False))

    elif margin >= -30:
        # ── SOFT FAIL — slip, no movement ────────────────────────────────────
        msg = random.choice(SLIP_MESSAGES)
        await session.send_line(colorize(msg, TextPresets.WARNING))

        # Minor damage on a bad slip
        if margin < -15:
            damage = random.randint(1, 5)
            session.health_current = max(0, session.health_current - damage)
            await session.send_line(
                colorize(f"  You scrape yourself for {damage} points of damage.", TextPresets.COMBAT_DAMAGE_TAKEN)
            )

        rt = apply_roundtime_effects(3, server, session)
        session.set_roundtime(rt)

        if climbing_ranks == 0:
            await session.send_line(
                colorize("  Training in Climbing would help greatly here.", TextPresets.SYSTEM)
            )

    else:
        # ── HARD FAIL — fall ─────────────────────────────────────────────────
        fall_msg = random.choice(FALL_MESSAGES)
        await session.send_line(colorize(fall_msg, TextPresets.COMBAT_CRIT))

        # Fall damage: 1d10 + level-based bonus
        fall_damage = random.randint(1, 10) + max(0, session.level - 1)
        session.health_current = max(0, session.health_current - fall_damage)
        session.position = "lying"

        await session.send_line(
            colorize(f"  You take {fall_damage} points of damage from the fall!", TextPresets.COMBAT_DAMAGE_TAKEN)
        )
        await session.send_line(
            colorize("  You are lying on the ground.", TextPresets.WARNING)
        )

        rt = apply_roundtime_effects(5, server, session)
        session.set_roundtime(rt)

        if session.health_current <= 0:
            await session.send_line(colorize("You have been knocked unconscious!", TextPresets.COMBAT_DEATH))
            session.position = "lying"


async def cmd_swim(session, cmd, args, server):
    """
    SWIM <target> - Attempt to traverse a swim exit with a Swimming skill check.
    """
    room = session.current_room
    if not room:
        await session.send_line("You can't do that right now.")
        return

    if session.position != "standing":
        await session.send_line("You need to stand up first.")
        return

    raw_target = (args or "").strip().lower()
    target = normalize_exit_key(raw_target)
    display_target = raw_target or target.replace("_", " ")
    if not target:
        swims = [k[5:].replace("_", " ") for k in room.exits if k.startswith("swim_")]
        if swims:
            await session.send_line(f"Swim where?  Options here: {', '.join(swims)}")
        else:
            await session.send_line("There is nowhere obvious to swim here.")
        return

    exit_key = f"swim_{target}"
    target_room_id = room.exits.get(exit_key)
    if target_room_id is None:
        await session.send_line(f"You don't see any water route toward '{display_target}' here.")
        return

    target_room = server.world.get_room(target_room_id)
    if not target_room:
        await session.send_line("That way leads nowhere... (room not loaded)")
        return

    skills = getattr(session, "skills", {}) or {}
    swim_data = skills.get(SKILL_SWIMMING, {})
    pf_data = skills.get(SKILL_PHYSICAL_FITNESS, {})
    swim_ranks = swim_data.get("ranks", 0) if isinstance(swim_data, dict) else 0
    pf_ranks = pf_data.get("ranks", 0) if isinstance(pf_data, dict) else 0

    str_bonus = _get_stat_bonus(getattr(session, "stat_strength", 50))
    con_bonus = _get_stat_bonus(getattr(session, "stat_constitution", 50))
    dex_bonus = _get_stat_bonus(getattr(session, "stat_dexterity", 50)) // 2
    swim_bonus = _get_skill_bonus(swim_ranks)
    pf_bonus = _get_skill_bonus(pf_ranks) // 5
    encumb_pen = _get_encumbrance_penalty(session)
    armor_pen = _get_armor_penalty(session)
    difficulty = _get_swim_difficulty(target)

    roll = _open_d100()
    buffs = get_active_buff_totals(server, session)
    total_bonus = swim_bonus + pf_bonus + str_bonus + con_bonus + dex_bonus - encumb_pen - armor_pen
    if buffs.get("movement_bonus"):
        total_bonus += 10
    result = roll + total_bonus
    margin = result - difficulty

    log.debug(
        "SWIM %s: roll=%d bonus=%d (swim=%d pf=%d str=%d con=%d dex=%d enc=-%d armor=-%d) result=%d difficulty=%d",
        display_target, roll, total_bonus, swim_bonus, pf_bonus,
        str_bonus, con_bonus, dex_bonus, encumb_pen, armor_pen, result, difficulty
    )

    if swim_ranks >= 50:
        margin = max(margin, 1)

    if margin > 0:
        if margin >= 40:
            await session.send_line(colorize(
                f"You cut through the water toward {display_target} with powerful strokes.",
                TextPresets.SYSTEM
            ))
            rt = 2
        elif margin >= 15:
            await session.send_line(colorize(
                f"You swim toward {display_target}.",
                TextPresets.SYSTEM
            ))
            rt = 3
        else:
            await session.send_line(colorize(
                f"You labor through the water and finally reach {display_target}.",
                TextPresets.SYSTEM
            ))
            rt = 4

        rt = apply_roundtime_effects(rt, server, session)
        session.set_roundtime(rt)
        await _move_player(session, room, target_room, f"swimming toward {display_target}", server, sneaking=False)
        return

    await session.send_line(colorize(
        random.choice(SWIM_FAIL_MESSAGES),
        TextPresets.WARNING
    ))

    if margin <= -35:
        damage = random.randint(3, 8)
        session.health_current = max(1, session.health_current - damage)
        await session.send_line(colorize(
            f"You are battered by the water and take {damage} damage.",
            TextPresets.WARNING
        ))
        if server.db and session.character_id:
            server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver
            )
        rt = apply_roundtime_effects(5, server, session)
        session.set_roundtime(rt)
        return

    rt = apply_roundtime_effects(3, server, session)
    session.set_roundtime(rt)
