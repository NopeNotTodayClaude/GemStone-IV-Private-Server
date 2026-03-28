"""
Combat commands - ATTACK, AMBUSH, HIDE, STANCE, KILL, SEARCH, SKIN, LOOT, AIM
Full GS4-style HIDE system with skill checks, perception, shadows, creature detection.
LOOT and SKIN auto-stow items into containers with space checks.
AIM sets a persistent body-location targeting preference per GS4 wiki (AIM verb).
"""

import logging
import random
import time
from server.core.protocol.colors import (
    colorize, TextPresets, creature_name as fmt_creature_name,
    roundtime_msg, item_name as fmt_item_name, combat_damage, combat_crit, combat_death
)
from server.core.commands.player.inventory import (
    _get_container_contents,
    _get_worn_containers,
    _is_skinning_sheath,
    _find_best_stow_container,
    _match_target,
    auto_stow_item,
    cmd_get,
    cmd_open,
    cmd_put,
    cmd_stow,
    cmd_swap,
)
from server.core.engine.magic_effects import apply_roundtime_effects, get_active_buff_totals
from server.core.engine.treasure import generate_coins, generate_gem, generate_box, generate_scroll
from server.core.engine.skinning import (
    can_remove_corpse,
    find_best_skinning_tool,
    is_skinning_tool,
    resolve_skinning,
)
from server.core.scripting.loaders.body_types_loader import get_aimable, resolve_aim

log = logging.getLogger(__name__)

SKILL_RANGED = 8
SKILL_THROWN = 9
SKILL_MOC = 12
SKILL_ARCANE_SYMBOLS = 15
SKILL_MIU = 16
SKILL_EMC = 19
SKILL_SMC = 20
SKILL_MMC = 21
SKILL_STALKING = 26
SKILL_AMBUSH = 43

_ROGUE_STUNMAN_TIERS = {
    "shield": 1,
    "weapon": 10,
    "get": 20,
    "stand": 32,
    "stance": 40,
    "attack": 50,
    "move": 63,
    "flee": 63,
    "hide": 63,
}

_ROGUE_CHEAPSHOTS = {
    "footstomp": {
        "rank": 1,
        "stamina": 6,
        "difficulty": 62,
        "effects": (("prone", 8), ("rooted", 8)),
        "hit": "You stamp down viciously on {target}, stealing its footing!",
        "room": "{name} stamps down viciously on {target}!",
    },
    "nosetweak": {
        "rank": 10,
        "stamina": 7,
        "difficulty": 66,
        "effects": (("disoriented", 12), ("dazed", 8)),
        "hit": "You snap a painful tweak across {target}'s face and leave it reeling!",
        "room": "{name} snaps a dirty nosetweak across {target}'s face!",
    },
    "templeshot": {
        "rank": 20,
        "stamina": 8,
        "difficulty": 72,
        "effects": (("stunned", 5), ("staggered", 10)),
        "hit": "You clip {target} at the temple with a practiced dirty strike!",
        "room": "{name} clips {target} at the temple with a practiced dirty strike!",
    },
    "eyepoke": {
        "rank": 54,
        "stamina": 9,
        "difficulty": 78,
        "effects": (("blinded", 12), ("disoriented", 12)),
        "hit": "You rake a vicious eyepoke across {target}'s vision!",
        "room": "{name} rakes a vicious eyepoke across {target}'s face!",
    },
    "throatchop": {
        "rank": 63,
        "stamina": 10,
        "difficulty": 82,
        "effects": (("silenced", 12), ("stunned", 6)),
        "hit": "You drive a brutal throatchop into {target} and steal its voice!",
        "room": "{name} drives a brutal throatchop into {target}!",
    },
}


def _rogue_guild_skill_ranks(session, skill_name: str) -> int:
    membership = getattr(session, "guild_membership", None) or {}
    if membership.get("guild_id") != "rogue":
        return 0
    skill_row = (getattr(session, "guild_skills", {}) or {}).get(skill_name, {})
    return int(skill_row.get("ranks", 0) or 0)


def _open_d100() -> int:
    roll = random.randint(1, 100)
    if roll >= 96:
        roll += random.randint(1, 100)
    elif roll <= 5:
        roll -= random.randint(1, 100)
    return roll


def _stat_bonus(session, stat_name: str) -> int:
    return (int(getattr(session, stat_name, 50) or 50) - 50) // 2


def _skill_row(session, skill_id: int) -> dict:
    skills = getattr(session, "skills", {}) or {}
    row = skills.get(skill_id, {})
    return row if isinstance(row, dict) else {}


def _skill_ranks(session, skill_id: int) -> int:
    return int(_skill_row(session, skill_id).get("ranks", 0) or 0)


def _skill_bonus(session, skill_id: int) -> int:
    row = _skill_row(session, skill_id)
    bonus = int(row.get("bonus", 0) or 0)
    return bonus if bonus else _skill_ranks(session, skill_id) * 3


def _match_item(item, needle: str) -> bool:
    target = (needle or "").strip().lower()
    if not target:
        return True
    for key in ("name", "short_name", "noun", "base_name"):
        value = str(item.get(key, "") or "").lower()
        if target and target in value:
            return True
    return False


def _find_inventory_item(session, *, predicate, needle=""):
    for hand_name in ("right_hand", "left_hand"):
        item = getattr(session, hand_name, None)
        if item and predicate(item) and _match_item(item, needle):
            return item, hand_name
    for item in getattr(session, "inventory", []) or []:
        if predicate(item) and _match_item(item, needle):
            return item, None
    return None, None


def _get_missile_weapon(session):
    for hand_name in ("right_hand", "left_hand"):
        item = getattr(session, hand_name, None)
        if item and item.get("item_type") == "weapon":
            cat = (item.get("weapon_category", "") or "").lower()
            if cat in ("ranged", "thrown"):
                return item, hand_name
    return None, None


def _expected_ammo_type(weapon) -> str:
    if not weapon:
        return ""
    noun = str(weapon.get("noun", "") or "").lower()
    base = str(weapon.get("base_name", "") or "").lower()
    short_name = str(weapon.get("short_name", "") or "").lower()
    if "crossbow" in noun or "crossbow" in base or "crossbow" in short_name:
        return "bolt"
    if (weapon.get("weapon_category", "") or "").lower() == "ranged":
        return "arrow"
    return "thrown"


def _consume_item_instance(session, item, hand_name, server) -> bool:
    if not item:
        return False
    inv_id = item.get("inv_id")
    if hand_name:
        setattr(session, hand_name, None)
    session.inventory = [row for row in (session.inventory or []) if row.get("inv_id") != inv_id]
    if inv_id and getattr(server, "db", None):
        server.db.remove_item_from_inventory(inv_id)
    return True


def _consume_stack_item(session, item, amount: int, server) -> bool:
    if not item or amount <= 0:
        return False
    inv_id = item.get("inv_id")
    qty = int(item.get("quantity", 1) or 1)
    if qty <= amount:
        session.inventory = [row for row in (session.inventory or []) if row.get("inv_id") != inv_id]
        if getattr(session, "ready_ammo_inv_id", None) == inv_id:
            session.ready_ammo_inv_id = None
            session.ready_ammo_type = None
            session.ready_ammo_name = None
        if inv_id and getattr(server, "db", None):
            server.db.remove_item_from_inventory(inv_id)
    else:
        item["quantity"] = qty - amount
        if inv_id and getattr(server, "db", None):
            server.db.execute_update(
                "UPDATE character_inventory SET quantity = %s WHERE id = %s",
                (item["quantity"], inv_id),
            )
    return True


def _find_ready_ammo(session, ammo_type: str):
    ready_inv_id = getattr(session, "ready_ammo_inv_id", None)
    if ready_inv_id:
        for item in getattr(session, "inventory", []) or []:
            if item.get("inv_id") == ready_inv_id and (item.get("ammo_type") or "") == ammo_type:
                return item
    for hand_name in ("right_hand", "left_hand"):
        item = getattr(session, hand_name, None)
        if item and item.get("item_type") == "ammo" and (item.get("ammo_type") or "") == ammo_type:
            return item
    for item in getattr(session, "inventory", []) or []:
        if item.get("item_type") == "ammo" and (item.get("ammo_type") or "") == ammo_type:
            return item
    return None


def _resolve_combat_target(session, server, raw_target):
    if raw_target:
        return server.creatures.find_creature_in_room(session.current_room.id, raw_target)
    if session.target and not session.target.is_dead:
        return session.target
    return None


async def _perform_missile_attack(session, creature, weapon, server, *, verb, skill_id, ds_attr, aimed_location=None, as_bonus=0):
    combat = getattr(server, "combat", None)
    if not combat:
        await session.send_line("Combat is unavailable right now.")
        return False

    dex_bonus = _stat_bonus(session, "stat_dexterity")
    cm_bonus = _skill_ranks(session, 4) // 2
    skill_bonus = _skill_bonus(session, skill_id)
    enchant = int(weapon.get("enchant_bonus", 0) or 0)
    attack_bonus = int(weapon.get("attack_bonus", 0) or 0)
    stance_mult = getattr(combat, "_STANCE_WEAPON_PCT", {}).get(session.stance, 0.70)
    raw_as = dex_bonus + cm_bonus + skill_bonus + enchant + attack_bonus + as_bonus
    player_as = int(raw_as * stance_mult)
    creature_ds = int(getattr(creature, ds_attr, getattr(creature, "ds_ranged", 20)) or 20)

    d100 = random.randint(1, 100)
    location, aim_succeeded = combat._resolve_hit_location(
        session, creature, aimed_location_override=aimed_location, hidden_ambush=False
    )
    from server.core.engine.combat.combat_engine import (
        CRIT_DIVISORS, CRIT_MESSAGES, LETHAL_THRESHOLDS,
        _resolve_damage_profile, LOCATION_DAMAGE_MULT, LOCATION_CRIT_DIV_MULT,
        SEVERABLE_LOCATIONS,
    )
    profile = _resolve_damage_profile(
        weapon.get("damage_type", "puncture"),
        getattr(creature, "armor_asg", 5),
        weapon.get("damage_factor", 0) or None,
    )
    damage_type = profile["damage_type"]
    avd = profile["avd"]
    weapon_df = profile["df"]
    endroll = d100 + player_as - creature_ds + avd

    weapon_name = weapon.get("short_name") or weapon.get("name") or "weapon"
    creature_display = fmt_creature_name(creature.full_name_with_level)
    swing_line = f"You {verb} {weapon_name} at {creature_display}!"
    roll_line = (
        f"  AS: {'+' if player_as >= 0 else ''}{player_as} vs "
        f"DS: {'+' if creature_ds >= 0 else ''}{creature_ds} with "
        f"AvD: {'+' if avd >= 0 else ''}{avd} + d100 roll: +{d100} = "
        f"{'+' if endroll >= 0 else ''}{endroll}"
    )

    if endroll <= 100:
        await session.send_line(swing_line)
        await session.send_line(colorize(roll_line, TextPresets.COMBAT_MISS))
        await session.send_line("  The shot goes wide.")
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} {verb}s at {creature.full_name} but misses!\n  {roll_line}",
            exclude=session,
        )
        rt = int(weapon.get("weapon_speed", 5) or 5) + 1
        rt = apply_roundtime_effects(rt, server, session, is_bolt=(skill_id == SKILL_RANGED))
        rt = max(3, min(12, rt))
        session.set_roundtime(rt)
        await session.send_line(roundtime_msg(rt))
        return False

    loc_df_mult = LOCATION_DAMAGE_MULT.get(location, 1.0)
    raw_damage = max(1, int((endroll - 100) * weapon_df * loc_df_mult))
    crit_divisor = max(1, int(CRIT_DIVISORS.get(getattr(creature, "armor_asg", 5), 5) * LOCATION_CRIT_DIV_MULT.get(location, 1.0)))
    crit_rank_max = min(9, raw_damage // crit_divisor)
    crit_rank = random.randint(max(1, (crit_rank_max + 1) // 2), crit_rank_max) if crit_rank_max > 0 else 0
    hp_damage = max(1, int((endroll - 100) * (0.42 + (weapon_df * 0.25)) * loc_df_mult) + crit_rank * 3)
    actual_damage = creature.take_damage(hp_damage)

    await session.send_line(swing_line)
    await session.send_line(colorize(roll_line, TextPresets.COMBAT_HIT))
    await session.send_line(colorize(
        f"  ... and hit for {actual_damage} points of damage!",
        TextPresets.COMBAT_HIT,
    ))
    if aimed_location and not aim_succeeded:
        await session.send_line(colorize(
            f"  Your aim drifts â€” striking the {location} instead!",
            TextPresets.SYSTEM,
        ))
    await session.send_line(combat_damage(actual_damage, location))
    if crit_rank > 0:
        crit_msgs = CRIT_MESSAGES.get(damage_type, CRIT_MESSAGES["puncture"])
        await session.send_line(combat_crit(crit_rank, crit_msgs.get(crit_rank, "Critical hit!")))
    if crit_rank >= 1:
        old_sev = creature.wounds.get(location, 0)
        new_sev = creature.apply_wound(location, crit_rank)
        if new_sev > old_sev:
            impairment = creature.evaluate_combat_impairment(location, old_sev, new_sev)
            if impairment.get("dropped_weapon"):
                await session.send_line(colorize(
                    f"  {creature.full_name.capitalize()} drops its weapon!",
                    TextPresets.COMBAT_HIT,
                ))
            if impairment.get("severed") and location in SEVERABLE_LOCATIONS:
                await session.send_line(colorize(
                    f"  The shot severs {creature.full_name}'s {location}!",
                    TextPresets.COMBAT_HIT,
                ))
            if impairment.get("stance_shift"):
                creature.stance = impairment["stance_shift"]
    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} {verb}s at {creature.full_name} and connects!\n"
        f"  {roll_line}\n"
        f"  Hit for {actual_damage} points of damage to the {location}.",
        exclude=session,
    )

    killed = False
    if creature.is_dead or crit_rank >= LETHAL_THRESHOLDS.get(location, 99):
        if not creature.is_dead:
            creature.take_damage(creature.health_current)
        killed = True
        await session.send_line(combat_death(creature.full_name.capitalize()))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"  {creature.full_name.capitalize()} falls to the ground dead!",
            exclude=session,
        )
        server.creatures.mark_dead(creature)
        session.target = None
        remaining = [
            c for c in server.creatures.get_creatures_in_room(session.current_room.id)
            if c.alive and c.aggressive and c is not creature
        ]
        if not remaining:
            from server.core.engine.combat.combat_engine import _exit_combat
            _exit_combat(server, session)
        if hasattr(server, "experience"):
            from server.core.commands.player.party import award_party_kill_xp
            await award_party_kill_xp(session, creature, server)
    else:
        from server.core.engine.combat.combat_engine import _enter_combat, _refresh_combat
        _enter_combat(server, session, creature)
        _refresh_combat(server, session, creature)

    rt = int(weapon.get("weapon_speed", 5) or 5) + (1 if skill_id == SKILL_RANGED else 0)
    rt = apply_roundtime_effects(rt, server, session, is_bolt=(skill_id == SKILL_RANGED))
    rt = max(3, min(12, rt))
    session.set_roundtime(rt)
    await session.send_line(roundtime_msg(rt))
    return killed


def _rogue_maneuver_score(session, skill_ranks: int, *, use_hide=False) -> int:
    score = _open_d100()
    score += skill_ranks * 5
    score += int(getattr(session, "level", 1) or 1) * 2
    score += _stat_bonus(session, "stat_dexterity")
    score += _stat_bonus(session, "stat_agility")
    if use_hide and getattr(session, "hidden", False):
        score += 25
    return score


def _find_creature_target(session, target_name, server):
    if target_name:
        return server.creatures.find_creature_in_room(session.current_room.id, target_name)
    if session.target and not session.target.is_dead:
        return session.target
    return None


def _spend_stamina(session, server, amount: int) -> bool:
    if int(getattr(session, "stamina_current", 0) or 0) < amount:
        return False
    session.stamina_current = max(0, int(session.stamina_current) - amount)
    if getattr(server, "db", None) and getattr(session, "character_id", None):
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver,
        )
    return True


def _apply_status(server, target, effect_id: str, duration: float):
    status = getattr(server, "status", None)
    if status:
        status.apply(target, effect_id, duration=duration)
        return
    if effect_id == "stunned" and hasattr(target, "stun"):
        target.stun(duration)
    elif effect_id == "prone":
        setattr(target, "prone", True)
    elif effect_id == "immobile":
        setattr(target, "immobilized", True)


async def cmd_sweep(session, cmd, args, server):
    """SWEEP <target> - Rogue guild maneuver that knocks a foe prone."""
    status = getattr(server, "status", None)
    if status and status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK or STUNMAN STAND if you have the training for it.")
        return
    skill_ranks = _rogue_guild_skill_ranks(session, "Sweep")
    if skill_ranks <= 0:
        await session.send_line("You lack the Rogue Guild training to execute a sweep.")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return
    if not args:
        await session.send_line("Sweep what?")
        return
    if not _spend_stamina(session, server, 8):
        await session.send_line("You are too tired to attempt a sweep right now.")
        return

    creature = _find_creature_target(session, args.strip(), server)
    if not creature:
        await session.send_line(f"You don't see any '{args.strip()}' here.")
        return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    score = _rogue_maneuver_score(session, skill_ranks)
    difficulty = 65 + int(getattr(creature, "level", 1) or 1) * 6 + max(0, creature.get_melee_ds() // 5)
    margin = score - difficulty

    if margin >= 0:
        _apply_status(server, creature, "prone", 12)
        _apply_status(server, creature, "staggered", 12)
        await session.send_line(colorize(
            f"You duck in low and sweep {creature.full_name} off its feet!",
            TextPresets.COMBAT_HIT
        ))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} sweeps {creature.full_name} off its feet!",
            exclude=session,
        )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "sweep_success")
    else:
        await session.send_line(colorize(
            f"You lunge for {creature.full_name}, but fail to unbalance it.",
            TextPresets.WARNING
        ))

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_subdue(session, cmd, args, server):
    """SUBDUE <target> - Rogue guild setup maneuver from hiding."""
    status = getattr(server, "status", None)
    if status and status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK if you have the training for it.")
        return
    skill_ranks = _rogue_guild_skill_ranks(session, "Subdue")
    if skill_ranks <= 0:
        await session.send_line("You lack the Rogue Guild training to subdue a target.")
        return
    if not getattr(session, "hidden", False):
        await session.send_line("You need to be hidden first!  Try HIDE.")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return
    if not args:
        await session.send_line("Subdue what?")
        return
    if not getattr(session, "right_hand", None):
        await session.send_line("You need a weapon or similar item ready in your right hand to subdue a foe.")
        return
    if not _spend_stamina(session, server, 9):
        await session.send_line("You are too tired to attempt a subdue right now.")
        return

    creature = _find_creature_target(session, args.strip(), server)
    if not creature:
        await session.send_line(f"You don't see any '{args.strip()}' here.")
        return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    session.hidden = False
    session.sneaking = False

    score = _rogue_maneuver_score(session, skill_ranks, use_hide=True)
    difficulty = 70 + int(getattr(creature, "level", 1) or 1) * 6 + max(0, creature.get_melee_ds() // 6)
    margin = score - difficulty

    if margin >= 0:
        _apply_status(server, creature, "vulnerable", 15)
        if margin >= 10:
            _apply_status(server, creature, "prone", 10)
        if margin >= 20 or skill_ranks >= 3:
            _apply_status(server, creature, "stunned", 5)
        if margin >= 35 or skill_ranks >= 5:
            _apply_status(server, creature, "immobile", 8)

        await session.send_line(colorize(
            f"You spring from hiding and subdue {creature.full_name} with a sharp, controlled strike!",
            TextPresets.COMBAT_HIT
        ))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} springs from hiding and subdues {creature.full_name}!",
            exclude=session,
        )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "subdue_success")
    else:
        await session.send_line(colorize(
            f"You spring from hiding and try to subdue {creature.full_name}, but the opening is not there.",
            TextPresets.WARNING
        ))

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_cheapshot(session, cmd, args, server):
    """CHEAPSHOT [maneuver] <target> - Rogue Guild dirty fighting."""
    status = getattr(server, "status", None)
    if status and status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK if you have the training for it.")
        return
    skill_ranks = _rogue_guild_skill_ranks(session, "Cheapshots")
    if skill_ranks <= 0:
        await session.send_line("You lack the Rogue Guild training to land a proper cheapshot.")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return
    if not args:
        available = [name for name, data in _ROGUE_CHEAPSHOTS.items() if skill_ranks >= data["rank"]]
        await session.send_line("Available cheapshots: " + ", ".join(available))
        return

    parts = args.strip().split(None, 1)
    candidate = parts[0].lower()
    if candidate in _ROGUE_CHEAPSHOTS:
        maneuver = candidate
        target_arg = parts[1] if len(parts) > 1 else ""
    else:
        maneuver = "footstomp"
        target_arg = args.strip()

    data = _ROGUE_CHEAPSHOTS.get(maneuver)
    if not data:
        await session.send_line("That is not a recognized cheapshot maneuver.")
        return
    if skill_ranks < data["rank"]:
        await session.send_line(f"You need rank {data['rank']} in Cheapshots before you can use {maneuver.upper()}.")
        return
    if not target_arg.strip():
        await session.send_line("Cheapshot whom?")
        return
    if not _spend_stamina(session, server, int(data["stamina"])):
        await session.send_line("You are too tired to attempt that cheapshot right now.")
        return

    creature = _find_creature_target(session, target_arg.strip(), server)
    if not creature:
        await session.send_line(f"You don't see any '{target_arg.strip()}' here.")
        return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    score = _rogue_maneuver_score(session, skill_ranks, use_hide=getattr(session, "hidden", False))
    difficulty = int(data["difficulty"]) + int(getattr(creature, "level", 1) or 1) * 5 + max(0, creature.get_melee_ds() // 6)
    margin = score - difficulty
    target_name = creature.full_name

    if margin >= 0:
        for effect_id, duration in data["effects"]:
            _apply_status(server, creature, effect_id, duration)
        _apply_status(server, creature, "vulnerable", 10)
        await session.send_line(colorize(data["hit"].format(target=target_name), TextPresets.COMBAT_HIT))
        await server.world.broadcast_to_room(
            session.current_room.id,
            data["room"].format(name=session.character_name, target=target_name),
            exclude=session,
        )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "cheapshot_success")
    else:
        await session.send_line(colorize(f"You lunge in with a dirty trick, but {target_name} slips clear of it.", TextPresets.WARNING))

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_stunman(session, cmd, args, server):
    """STUNMAN <action> - Attempt to act through a stun using Rogue Guild training."""
    skill_ranks = _rogue_guild_skill_ranks(session, "Stun Maneuvers")
    if skill_ranks <= 0:
        await session.send_line("You lack the Rogue Guild training to fight through a stun.")
        return

    status = getattr(server, "status", None)
    is_stunned = status.has(session, "stunned") if status else False
    if not is_stunned:
        await session.send_line("You are not stunned right now.")
        return
    if not args:
        await session.send_line("Use STUNMAN with one of: shield, weapon, get, stand, stance, attack, move, flee, hide.")
        return
    if not _spend_stamina(session, server, 10):
        await session.send_line("You are too tired to force an action through the stun.")
        return

    parts = args.strip().split(None, 1)
    subcmd = parts[0].lower()
    remainder = parts[1] if len(parts) > 1 else ""
    required_rank = _ROGUE_STUNMAN_TIERS.get(subcmd)
    if required_rank is None:
        await session.send_line("Use STUNMAN with one of: shield, weapon, get, stand, stance, attack, move, flee, hide.")
        return
    if skill_ranks < required_rank:
        await session.send_line(f"You need rank {required_rank} in Stun Maneuvers before you can use that option.")
        return

    score = _open_d100() + skill_ranks * 10 + _stat_bonus(session, "stat_discipline") + _stat_bonus(session, "stat_agility")
    difficulty = {
        "shield": 75,
        "weapon": 75,
        "get": 80,
        "stand": 85,
        "stance": 85,
        "attack": 95,
        "move": 100,
        "flee": 100,
        "hide": 100,
    }.get(subcmd, 85)
    if score < difficulty:
        await session.send_line(colorize("You struggle against the stun, but cannot complete the maneuver.", TextPresets.WARNING))
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    success = False
    if status and status.has(session, "stunned"):
        status.remove(session, "stunned")
    if subcmd == "stand":
        from server.core.commands.player.actions import cmd_stand
        await cmd_stand(session, "stand", "", server)
        success = True
    elif subcmd == "stance":
        desired = "guarded" if skill_ranks < 60 else "defensive"
        await cmd_stance(session, "stance", desired, server)
        success = True
    elif subcmd == "attack":
        await cmd_attack(session, "attack", remainder, server)
        success = True
    elif subcmd == "get":
        from server.core.commands.player.inventory import cmd_get
        await cmd_get(session, "get", remainder, server)
        success = True
    elif subcmd == "move":
        from server.core.commands.player.movement import cmd_move, cmd_go
        move_target = (remainder or "").strip().lower()
        if not move_target:
            await session.send_line("Move where?")
        elif move_target in {"north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down", "out"}:
            await cmd_move(session, move_target, "", server)
            success = True
        else:
            await cmd_go(session, "go", move_target, server)
            success = True
    elif subcmd == "flee":
        room = getattr(session, "current_room", None)
        if room and room.exits:
            safe_exit = None
            for direction, target_room_id in room.exits.items():
                if server.creatures.get_creatures_in_room(target_room_id):
                    continue
                safe_exit = direction
                break
            if safe_exit:
                from server.core.commands.player.movement import cmd_move, cmd_go
                if safe_exit in {"north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down", "out"}:
                    await cmd_move(session, safe_exit, "", server)
                else:
                    await cmd_go(session, "go", safe_exit, server)
                success = True
            else:
                await session.send_line("No clean escape route presents itself.")
    elif subcmd == "hide":
        await cmd_hide(session, "hide", "", server)
        success = True
    elif subcmd == "weapon":
        if getattr(session, "right_hand", None):
            await session.send_line("You already have a weapon readied in your right hand.")
            success = True
        else:
            wieldable = next((item for item in session.inventory if item.get("item_type") in {"weapon", "sword", "dagger", "axe", "mace", "club"}), None)
            if wieldable:
                wieldable["slot"] = "right_hand"
                session.right_hand = wieldable
                await session.send_line(colorize(f"You wrench {wieldable.get('name', 'a weapon')} into your right hand despite the stun.", TextPresets.COMBAT_HIT))
                success = True
            else:
                await session.send_line("You do not have a suitable weapon ready to grab.")
    elif subcmd == "shield":
        if getattr(session, "left_hand", None):
            await session.send_line("You already have something ready in your left hand.")
            success = True
        else:
            shield = next((item for item in session.inventory if item.get("noun", "").lower() == "shield" or item.get("item_type") == "shield"), None)
            if shield:
                shield["slot"] = "left_hand"
                session.left_hand = shield
                await session.send_line(colorize(f"You drag {shield.get('name', 'your shield')} into your left hand despite the stun.", TextPresets.COMBAT_HIT))
                success = True
            else:
                await session.send_line("You do not have a shield ready to grab.")

    if success and getattr(server, "guild", None):
        await server.guild.record_event(session, "stunman_success")


async def cmd_rgambit(session, cmd, args, server):
    """RGAMBIT [DIVERT] <target> - Rogue guild gambit support."""
    status = getattr(server, "status", None)
    if status and status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK if you have the training for it.")
        return
    skill_ranks = _rogue_guild_skill_ranks(session, "Rogue Gambits")
    if skill_ranks <= 0:
        await session.send_line("You lack the Rogue Guild training to attempt a rogue gambit.")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return
    raw_args = (args or "").strip()
    if (cmd or "").lower() == "divert":
        raw_args = f"divert {raw_args}".strip()
    if not raw_args:
        await session.send_line("Use RGAMBIT DIVERT <target>, or RGAMBIT TUMBLE/CARTWHEEL/FLIP/POSE.")
        return

    parts = raw_args.split(None, 1)
    gambit = parts[0].lower()
    target_arg = parts[1] if len(parts) > 1 else ""

    if gambit in {"tumble", "cartwheel", "flip", "pose", "display"}:
        if not _spend_stamina(session, server, 4):
            await session.send_line("You are too tired to work the room with a rogue gambit right now.")
            return
        text = {
            "tumble": "You tumble through a quick rogue flourish, ending in a low balanced crouch.",
            "cartwheel": "You throw yourself through a smooth cartwheel and come up grinning.",
            "flip": "You spring into a quick flip, landing light on your feet.",
            "pose": "You finish with a careful rogue's pose, equal parts mockery and confidence.",
            "display": "You make a quick, showy display of nerve and timing.",
        }[gambit]
        await session.send_line(colorize(text, TextPresets.STEALTH))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} executes a showy rogue gambit.",
            exclude=session,
        )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "rgambit_perform")
        session.set_roundtime(2)
        await session.send_line(roundtime_msg(2))
        return

    if not _spend_stamina(session, server, 8):
        await session.send_line("You are too tired to attempt a rogue gambit right now.")
        return

    if gambit not in {"divert"}:
        target_arg = raw_args
        gambit = "divert"

    creature = _find_creature_target(session, target_arg.strip(), server)
    if not creature:
        await session.send_line(f"You don't see any '{target_arg.strip()}' here.")
        return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    score = _rogue_maneuver_score(session, skill_ranks)
    difficulty = 70 + int(getattr(creature, "level", 1) or 1) * 6 + max(0, creature.get_melee_ds() // 5)
    margin = score - difficulty

    if margin >= 0:
        _apply_status(server, creature, "vulnerable", 15)
        _apply_status(server, creature, "disoriented", 12)
        if getattr(creature, "target", None) is session:
            creature.target = None
            creature.in_combat = False
        await session.send_line(colorize(
            f"You execute a diverting rogue gambit and throw {creature.full_name} off balance!",
            TextPresets.COMBAT_HIT
        ))
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} executes a rogue gambit against {creature.full_name}, throwing it off balance!",
            exclude=session,
        )
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "rgambit_perform")
            await server.guild.record_event(session, "rgambit_success")
    else:
        await session.send_line(colorize(
            f"You attempt a rogue gambit against {creature.full_name}, but it refuses to take the bait.",
            TextPresets.WARNING
        ))

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


# =============================================================================
# PERCEPTION HELPERS
# All values driven by server.perception_cfg (loaded from globals/perception.lua)
# =============================================================================

def _perception_roll(session, server) -> int:
    """
    Open-ended d100 + Perception skill bonus + INT bonus.
    Returns the total roll for this observer.
    """
    cfg   = getattr(server, "perception_cfg", {})
    sid   = cfg.get("skill_id", 27)
    rmult = cfg.get("rank_multiplier", 3)
    stat  = cfg.get("stat", "stat_intuition")
    sdiv  = cfg.get("stat_divisor", 2)

    skills   = getattr(session, "skills", {}) or {}
    sk_data  = skills.get(sid, {})
    ranks    = sk_data.get("ranks", 0) if isinstance(sk_data, dict) else 0
    sk_bonus = ranks * rmult

    stat_val  = getattr(session, stat, 50)
    stat_bonus = (stat_val - 50) // sdiv
    buffs = get_active_buff_totals(server, session)
    buff_bonus = int(buffs.get("perception_bonus", 0) or 0)

    base = random.randint(1, 100)
    if base >= 96:
        base += random.randint(1, 100)
    elif base <= 5:
        base -= random.randint(1, 10)

    return base + sk_bonus + stat_bonus + buff_bonus


def _room_perception_mod(room, cfg: dict) -> int:
    """Return the flat penalty that the room environment applies to observers."""
    if getattr(room, "dark", False):
        return cfg.get("dark_penalty", -20)
    if not getattr(room, "indoor", False):
        return cfg.get("outdoor_penalty", -10)
    return 0


async def _run_hide_perception_checks(session, room, hide_total: int, server):
    """
    After a successful HIDE attempt, every other non-hidden player in the room
    gets a Perception counter-roll.  If their roll beats the hider's total
    (accounting for the hider's built-in bonus), they see through the hide.

    Called only on success â€” failed hides are already visible.
    """
    cfg         = getattr(server, "perception_cfg", {})
    hider_bonus = cfg.get("hide_hider_bonus", 20)
    obs_mod     = cfg.get("hide_observer_mod", 0)
    hider_side  = hide_total + hider_bonus

    room_mod = _room_perception_mod(room, cfg)
    hider_name = session.character_name or "Someone"

    observers = server.world.get_players_in_room(room.id)
    for obs in observers:
        if obs is session:
            continue
        if getattr(obs, "hidden", False):
            continue  # hidden observers don't get to spot you either

        obs_roll = _perception_roll(obs, server) + obs_mod + room_mod

        if obs_roll >= hider_side:
            # Spotted â€” the observer can still see them
            await obs.send_line(
                colorize(
                    f"  You notice {hider_name} attempting to hide â€” and they don't quite manage it from your perspective.",
                    TextPresets.SYSTEM
                )
            )


# =========================================================
# ATTACK
# =========================================================

async def cmd_attack(session, cmd, args, server):
    """ATTACK <target> - Basic melee attack.
    If hidden, automatically uses ambush mechanics per GS4 rules.
    """
    _status = getattr(server, "status", None)
    if _status and _status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK if you have the training for it.")
        return
    if not args:
        if session.target and not session.target.is_dead:
            creature = session.target
        else:
            await session.send_line("What do you want to attack?")
            return
    else:
        target_name = args.strip()
        creature = server.creatures.find_creature_in_room(
            session.current_room.id, target_name
        )
        if not creature:
            await session.send_line(f"You don't see any '{target_name}' here to attack.")
            return

    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    # GS4: ATTACK from hiding automatically uses ambush mechanics
    if session.hidden:
        await cmd_ambush(session, cmd, args, server)
        return

    await server.combat.player_attacks_creature(session, creature)


async def cmd_kill(session, cmd, args, server):
    """KILL - alias for ATTACK."""
    await cmd_attack(session, cmd, args, server)


# =========================================================
# AMBUSH (from hiding)
# =========================================================

async def cmd_ambush(session, cmd, args, server):
    """AMBUSH [target] [location] - Attack from hiding with aimed strike."""
    _status = getattr(server, "status", None)
    if _status and _status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK if you have the training for it.")
        return
    if not session.hidden:
        await session.send_line("You need to be hidden first!  Try HIDE.")
        return

    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    raw_args = (args or "").strip()
    aimed_location = None
    creature = None

    if not raw_args:
        if session.target and not session.target.is_dead:
            creature = session.target
        else:
            await session.send_line("Ambush what?")
            return
    else:
        words = raw_args.split()
        for idx in range(len(words), 0, -1):
            candidate_name = " ".join(words[:idx])
            creature = server.creatures.find_creature_in_room(
                session.current_room.id, candidate_name
            )
            if creature:
                remainder = " ".join(words[idx:]).strip()
                aimed_location = remainder or None
                break

        if not creature and session.target and not session.target.is_dead:
            creature = session.target
            aimed_location = raw_args

        if not creature:
            await session.send_line(f"You don't see any '{raw_args}' here.")
            return

    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    # Unhide and stop sneaking on attack
    session.hidden = False
    session.sneaking = False

    # Ambush bonus from Stalking & Hiding skill (int ID 26)
    SKILL_STALKING = 26
    skills = getattr(session, 'skills', {}) or {}
    sh_data = skills.get(SKILL_STALKING, {})
    stalking_ranks = int(sh_data.get('ranks', 0)) if isinstance(sh_data, dict) else 0
    stalking_bonus = stalking_ranks * 3

    # Ambush skill doesn't exist as separate skill in GS4 â€” stalking drives it
    # Bonus scales with stalking ranks + level for rogues
    prof_id = getattr(session, 'profession_id', 0)
    level   = getattr(session, 'level', 1)
    if prof_id == 2:  # Rogue
        ambush_bonus = stalking_bonus + level * 3 + 10
    else:
        ambush_bonus = stalking_bonus + level * 2

    # Ambush from hiding gets a significant AS bonus
    hide_as_bonus = stalking_ranks * 2

    await session.send_line(colorize(
        f"You emerge from hiding and ambush {creature.full_name}!",
        TextPresets.COMBAT_HIT
    ))

    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} emerges from hiding and ambushes {creature.full_name}!",
        exclude=session
    )

    await server.combat.player_attacks_creature(
        session, creature,
        aimed_location=aimed_location,
        is_ambush=True
    )
    if getattr(server, "guild", None):
        await server.guild.record_event(session, "ambush_success")


# =========================================================
# HIDE - Full GS4 System
# =========================================================

async def cmd_hide(session, cmd, args, server):
    """HIDE - Attempt to hide in the shadows.

    GS4-accurate formula:
      open d100 + S&H skill bonus (ranks*3) + Discipline bonus (1:1)
      + profession bonus (Rogue: +level+3 from lvl20, +lvl before)
      + indoor/dark modifier
      - armor action penalty
      - creature detection modifier
      vs fixed difficulty of 100 (success if total >= 100)
    """
    if session.hidden:
        await session.send_line("You are already hidden.")
        return
    # Use StatusManager if available -- prevents "can't hide" after combat is cleared
    _status = getattr(server, 'status', None)
    if _status and _status.has(session, "stunned"):
        await session.send_line("You are stunned and cannot hide.")
        return
    _in_combat = _status.has(session, 'in_combat') if _status else session.in_combat
    if _in_combat:
        await session.send_line("You can't hide while in combat!")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    room = session.current_room
    if not room:
        return

    # â”€â”€ Skill lookup by integer ID â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    SKILL_STALKING = 26
    skills = getattr(session, 'skills', {}) or {}
    sh_data = skills.get(SKILL_STALKING, {})
    sh_ranks = sh_data.get('ranks', 0) if isinstance(sh_data, dict) else 0
    sh_bonus = sh_ranks * 3   # GS4: each rank = +3 bonus
    buffs = get_active_buff_totals(server, session)
    sh_bonus += int(buffs.get("stalking_hiding_bonus", 0) or 0)
    if buffs.get("movement_bonus"):
        sh_bonus += 10

    # Discipline is 1:1 bonus to hiding (per wiki)
    disc_val = getattr(session, 'stat_discipline', 50)
    disc_bonus = (disc_val - 50) // 2   # stat bonus formula

    # Profession bonus (per wiki)
    # Rogue: +level+3 from level 20; scales up to that
    # Ranger/Bard: +1/level capped at +20
    # Others: 0
    prof_id = getattr(session, 'profession_id', 0)
    level   = getattr(session, 'level', 1)
    if prof_id == 2:    # Rogue
        if level >= 20:
            prof_bonus = level + 3
        else:
            prof_bonus = level
    elif prof_id in (7, 8):  # Ranger, Bard
        prof_bonus = min(20, level)
    else:
        prof_bonus = 0

    # Room modifiers
    room_mod = 0
    if getattr(room, 'dark', False):
        room_mod += 20      # dark rooms are much easier to hide in
    elif not getattr(room, 'indoor', False):
        room_mod += 10      # outdoors easier (cover, shadows)
    elif getattr(room, 'safe', False):
        room_mod -= 15      # bright town centers hardest

    # Armor action penalty
    armor_pen = 0
    for item in session.inventory:
        if item.get('item_type') == 'armor' and item.get('slot') == 'torso':
            armor_pen += abs(item.get('action_penalty', 0) or 0)

    # Creature detection modifier â€” each hostile creature raises the difficulty
    # Empty room = no added difficulty at all (should be near auto-success)
    creature_difficulty = 0
    if hasattr(server, 'creatures'):
        creatures = server.creatures.get_creatures_in_room(room.id)
        for c in [x for x in creatures if x.alive and x.aggressive]:
            # Each creature raises difficulty based on their level vs yours
            creature_difficulty += max(10, (c.level - level) * 5 + 15)

    # â”€â”€ Open d100 roll â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    base_roll = random.randint(1, 100)
    # 5% explode high, 5% go negative (open d100)
    if base_roll >= 96:
        base_roll += random.randint(1, 100)
    elif base_roll <= 5:
        base_roll -= random.randint(1, 100)

    total = base_roll + sh_bonus + disc_bonus + prof_bonus + room_mod - armor_pen

    # Base difficulty is LOW for an empty room â€” hiding with no one watching is easy.
    # Creature presence raises it substantially.  This matches GS4: HIDE in empty
    # room with any skill should succeed the vast majority of the time; hiding in
    # front of hostile creatures is what gets hard.
    DIFFICULTY = 30 + creature_difficulty

    if total >= DIFFICULTY:
        session.hidden = True

        if getattr(room, 'dark', False):
            hide_msg = "You slip into the darkness and vanish from sight."
        elif getattr(room, 'indoor', False):
            hide_msg = "You attempt to blend into the shadows... success!"
        else:
            hide_msg = random.choice([
                "You attempt to blend into the shadows... success!",
                "You slip behind some cover and become hidden.",
                "You fade into the surrounding terrain.",
                "You press yourself into the shadows and vanish from sight.",
            ])

        await session.send_line(colorize(hide_msg, TextPresets.STEALTH))
        await server.world.broadcast_to_room(
            room.id,
            f"{session.character_name} fades into the shadows.",
            exclude=session
        )
        # Perception counter-roll â€” other players may see through the hide
        await _run_hide_perception_checks(session, room, total, server)
        if getattr(server, "guild", None):
            await server.guild.record_event(session, "hide_success")
    else:
        margin = DIFFICULTY - total
        if margin <= 20:
            fail_msg = "You attempt to blend into the shadows... but don't feel very confident about your success."
        else:
            fail_msg = random.choice([
                "You attempt to blend into the shadows, but fail.",
                "You try to hide but can't find adequate cover.",
                "You attempt to conceal yourself but are too exposed.",
            ])
        await session.send_line(colorize(fail_msg, TextPresets.WARNING))

    rt = 3
    session.set_roundtime(rt)
    await session.send_line(roundtime_msg(rt))


# =========================================================
# SNEAK
# =========================================================

async def cmd_sneak(session, cmd, args, server):
    """SNEAK - Toggle sneaking mode. While sneaking, movement rolls stealth
    instead of automatically breaking hide. You must be hidden first.
    """
    _status = getattr(server, 'status', None)
    if _status and _status.has(session, "stunned"):
        await session.send_line("You are stunned and cannot sneak.")
        return
    _in_combat = _status.has(session, 'in_combat') if _status else session.in_combat
    if _in_combat:
        await session.send_line("You can't sneak while in combat!")
        return

    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    currently_sneaking = getattr(session, 'sneaking', False)

    if currently_sneaking:
        session.sneaking = False
        await session.send_line(colorize("You stop sneaking.", TextPresets.STEALTH))
        return

    # Must be hidden first
    if not session.hidden:
        await session.send_line(colorize(
            "You must be hidden to sneak.  Attempting to hide first...",
            TextPresets.STEALTH
        ))
        await cmd_hide(session, cmd, args, server)
        if not session.hidden:
            return

    session.sneaking = True
    await session.send_line(colorize(
        "You move carefully, ready to sneak.  Each step will roll your stealth.",
        TextPresets.STEALTH
    ))


# =========================================================
# STANCE
# =========================================================

async def cmd_stance(session, cmd, args, server):
    """STANCE <stance> - Change combat stance."""
    valid_stances = ["offensive", "advance", "forward", "neutral", "guarded", "defensive"]

    if not args:
        await session.send_line(f"Current stance: {colorize(session.stance.capitalize(), TextPresets.SYSTEM)}")
        await session.send_line(f"Valid stances: {', '.join(s.capitalize() for s in valid_stances)}")
        return

    new_stance = args.strip().lower()
    if new_stance not in valid_stances:
        await session.send_line(f"Unknown stance.  Valid stances: {', '.join(s.capitalize() for s in valid_stances)}")
        return

    old_stance = session.stance
    session.stance = new_stance
    if getattr(server, "db", None) and getattr(session, "character_id", None):
        server.db.save_character(session)
    await session.send_line(f"You are now in a {colorize(new_stance.capitalize(), TextPresets.SYSTEM)} stance.  (was {old_stance.capitalize()})")


# =========================================================
# SEARCH
# =========================================================

async def cmd_search(session, cmd, args, server):
    """SEARCH - Search a dead creature for loot and scan the room for hidden exits."""
    room = session.current_room
    if not room:
        return

    search_target = str(args or "").strip().lower()
    search_key = "search"
    if search_target:
        normalized_target = search_target.replace("-", "_")
        normalized_target = "_".join(normalized_target.split())
        search_key = f"search_{normalized_target}"

    cfg = getattr(server, "perception_cfg", {})
    level = getattr(session, "level", 1)

    hidden = getattr(room, "hidden_exits", {})
    found_exits = []
    sensed_exits = []

    if hidden:
        room_mod = _room_perception_mod(room, cfg)
        level_bonus = int(level * cfg.get("search_level_mult", 0.5))
        sense_thresh = cfg.get("sense_threshold", 15)

        for key, he in hidden.items():
            trigger = str(he.get("search_trigger") or "search").strip().lower()
            if trigger != search_key:
                continue

            char_id = getattr(session, "character_id", None)
            revealed = getattr(room, "_revealed_hidden_exits", {})
            if char_id and char_id in revealed.get(key, set()):
                continue

            search_dc = he.get("search_dc", 20)
            perc_roll = _perception_roll(session, server) + room_mod + level_bonus

            if perc_roll >= search_dc:
                room.reveal_hidden_exit(key, session)
                custom_msg = he.get("message")
                display = key[3:] if key.startswith("go_") else key
                if custom_msg:
                    found_exits.append(custom_msg)
                else:
                    found_exits.append(
                        cfg.get("search_found_exit_msg", "Your careful search reveals a hidden path: ")
                        + display
                    )
            elif perc_roll >= (search_dc - sense_thresh):
                sensed_exits.append(key)

    if getattr(server, "guild", None):
        try:
            await server.guild.maybe_complete_search_bounty(session)
        except Exception:
            pass

    dead = server.creatures.get_dead_creatures_in_room(room.id)
    creature_searched = False
    found_items = []
    left_on_ground = []
    db = getattr(server, "db", None)
    loot_creature = None

    if dead:
        loot_creature = dead[0]
        await session.send_line(f"You search {loot_creature.full_name}...")

        if getattr(loot_creature, "searched", False):
            await session.send_line("  You find nothing more of value.")
        else:
            loot_creature.searched = True
            creature_searched = True

            loot = generate_treasure(db, loot_creature) if (generate_treasure and db) else None
            if loot:
                if loot.get("coins", 0) > 0:
                    session.silver += loot["coins"]
                    found_items.append(
                        f"  You find {colorize(str(loot['coins']) + ' silver coins', TextPresets.ITEM_NAME)}!"
                    )

                for item in loot.get("items", []):
                    item_id = item.get("item_id") or item.get("id")
                    if not item_id and db:
                        item_id = db.get_or_create_item(
                            name=item.get("name", "something"),
                            short_name=item.get("short_name", item.get("name", "something")),
                            noun=item.get("noun", "item"),
                            item_type=item.get("item_type", "misc"),
                            value=item.get("value", 0),
                            description=item.get("description", ""),
                        )
                    if item_id:
                        item["item_id"] = item_id

                    display = item.get("name") or item.get("short_name") or "something"
                    success, location, _ = auto_stow_item(session, server, item)
                    if success:
                        if item.get("item_type") == "container" and item.get("inv_id"):
                            _db_save_item_state(server, item["inv_id"], item)
                        found_items.append(
                            f"  You find {fmt_item_name(display)} and put it in your {location}."
                        )
                    else:
                        if hasattr(server, "world"):
                            server.world.add_ground_item(
                                room.id,
                                item,
                                dropped_by_character_id=session.character_id,
                                dropped_by_name=session.character_name,
                                source="loot",
                            )
                        else:
                            room._ground_items = getattr(room, "_ground_items", [])
                            room._ground_items.append(item)
                        left_on_ground.append(display)
                        found_items.append(f"  You find {fmt_item_name(display)}!")
            else:
                treasure = getattr(loot_creature, "treasure", {}) or {}
                c_level = int(getattr(loot_creature, "level", 1) or 1)

                if treasure.get("coins"):
                    coins = generate_coins(c_level)
                    session.silver += coins
                    found_items.append(
                        f"  You find {colorize(str(coins) + ' silver coins', TextPresets.ITEM_NAME)}!"
                    )

                if treasure.get("gems") and random.random() < 0.4:
                    gem = generate_gem(db, c_level) if db else _fallback_gem(c_level)
                    if gem:
                        if db and not gem.get("item_id"):
                            gem["item_id"] = db.get_or_create_item(
                                name=gem["name"],
                                short_name=gem.get("short_name", gem["name"]),
                                noun=gem.get("noun", "gem"),
                                item_type="gem",
                                value=gem.get("value", 50),
                                description=gem.get("description", f"A {gem.get('short_name', gem['name'])}."),
                            )
                        success, location, _ = auto_stow_item(session, server, gem)
                        if success:
                            found_items.append(
                                f"  You find {fmt_item_name(gem['name'])} and put it in your {location}."
                            )
                        else:
                            if hasattr(server, "world"):
                                server.world.add_ground_item(room.id, gem, source="loot")
                            else:
                                room._ground_items = getattr(room, "_ground_items", [])
                                room._ground_items.append(gem)
                            left_on_ground.append(gem["name"])
                            found_items.append(f"  You find {fmt_item_name(gem['name'])}!")

                if treasure.get("boxes") and random.random() < 0.3:
                    box = generate_box(db, c_level) if db else _fallback_box(c_level)
                    if box:
                        if db and not box.get("item_id"):
                            box["item_id"] = db.get_or_create_item(
                                name=box["name"],
                                short_name=box.get("short_name", box["name"]),
                                noun=box.get("noun", "box"),
                                item_type="container",
                                value=box.get("value", 30),
                                description=box.get("description", f"A {box.get('short_name', box['name'])}."),
                            )
                        success, location, _ = auto_stow_item(session, server, box)
                        if success:
                            if box.get("item_type") == "container" and box.get("inv_id"):
                                _db_save_item_state(server, box["inv_id"], box)
                            found_items.append(
                                f"  You find {fmt_item_name(box['name'])} and put it in your {location}."
                            )
                        else:
                            if hasattr(server, "world"):
                                server.world.add_ground_item(room.id, box, source="loot")
                            else:
                                room._ground_items = getattr(room, "_ground_items", [])
                                room._ground_items.append(box)
                            left_on_ground.append(box["name"])
                            found_items.append(f"  You find {fmt_item_name(box['name'])}!")

                if treasure.get("magic") and random.random() < 0.15:
                    scroll = generate_scroll(db, c_level) if db else None
                    if scroll:
                        if db and not scroll.get("item_id"):
                            scroll["item_id"] = db.get_or_create_item(
                                name=scroll["name"],
                                short_name=scroll.get("short_name", scroll["name"]),
                                noun=scroll.get("noun", "scroll"),
                                item_type="scroll",
                                value=scroll.get("value", 0),
                                description=scroll.get("description", ""),
                            )
                        success, location, _ = auto_stow_item(session, server, scroll)
                        if success:
                            found_items.append(
                                f"  You find {fmt_item_name(scroll['name'])} and put it in your {location}."
                            )
                        else:
                            if hasattr(server, "world"):
                                server.world.add_ground_item(room.id, scroll, source="loot")
                            else:
                                room._ground_items = getattr(room, "_ground_items", [])
                                room._ground_items.append(scroll)
                            left_on_ground.append(scroll["name"])
                            found_items.append(f"  You find {fmt_item_name(scroll['name'])}!")

    for msg in found_exits:
        await session.send_line(colorize(f"  {msg}", TextPresets.SYSTEM))

    if sensed_exits and not found_exits:
        await session.send_line(colorize(
            f"  {cfg.get('search_failed_exit_msg', 'You sense there may be something hidden here, but cannot quite make it out.')}",
            TextPresets.SYSTEM
        ))

    if loot_creature:
        if found_items:
            for line in found_items:
                await session.send_line(line)
        elif creature_searched:
            await session.send_line("  You find nothing of value.")

        if left_on_ground:
            for item_name in left_on_ground:
                await session.send_line(colorize(
                    f"  No space remaining - {item_name} was left on the ground.",
                    TextPresets.WARNING
                ))

        if creature_searched and hasattr(server, "experience"):
            await server.experience.collect_loot_xp(session, loot_creature)

        if can_remove_corpse(loot_creature):
            server.creatures.remove_creature(loot_creature)

        if db and session.character_id:
            db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver
            )
    elif not found_exits and not sensed_exits:
        await session.send_line(
            cfg.get("search_nothing_msg", "You search around carefully but find nothing hidden.")
        )

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))
# â”€â”€ Fallbacks when DB is unavailable â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# These mirror the tier tables in treasure.py so no-DB servers still get
# level-appropriate loot.

_GEM_FALLBACKS = {
    (1,  5):  [("a grey pearl",        "grey pearl",        "pearl",        30),
               ("a polished agate",    "polished agate",    "agate",        25),
               ("a rose quartz",       "rose quartz",       "quartz",       20)],
    (6,  10): [("a small ruby",        "small ruby",        "ruby",         80),
               ("a clear topaz",       "clear topaz",       "topaz",        70),
               ("a piece of jade",     "jade",              "jade",         60)],
    (11, 15): [("a blue sapphire",     "blue sapphire",     "sapphire",    150),
               ("a tiny emerald",      "tiny emerald",      "emerald",     120),
               ("a pale aquamarine",   "pale aquamarine",   "aquamarine",  100)],
    (16, 99): [("a bright diamond",    "bright diamond",    "diamond",     300),
               ("a deep amethyst",     "deep amethyst",     "amethyst",    250),
               ("a blood red garnet",  "blood red garnet",  "garnet",      200)],
}

_BOX_FALLBACKS = {
    (1,  5):  [("a wooden coffer",        "wooden coffer",        "coffer"),
               ("a dented iron box",      "dented iron box",      "box")],
    (6,  10): [("an iron coffer",         "iron coffer",          "coffer"),
               ("a small chest",          "small chest",          "chest")],
    (11, 15): [("a metal strongbox",      "metal strongbox",      "strongbox"),
               ("a small steel lockbox",  "small steel lockbox",  "lockbox")],
    (16, 99): [("a heavy steel trunk",    "heavy steel trunk",    "trunk"),
               ("an enruned strongbox",   "enruned strongbox",    "strongbox")],
}


def _tier(tiers, level):
    for (lo, hi), items in tiers.items():
        if lo <= level <= hi:
            return items
    return list(tiers.values())[-1]


def _fallback_gem(level):
    name, short, noun, value = random.choice(_tier(_GEM_FALLBACKS, level))
    return {"name": name, "short_name": short, "noun": noun,
            "item_type": "gem", "value": value}


def _fallback_box(level):
    import random as _r
    name, short, noun = _r.choice(_tier(_BOX_FALLBACKS, level))
    lock_diff = level * 15 + _r.randint(-10, 20)
    return {"name": name, "short_name": short, "noun": noun,
            "item_type": "container", "value": level * 10,
            "container_capacity": 3, "lock_difficulty": max(10, lock_diff),
            "is_locked": True}


# =========================================================
# SKIN - Auto-stow with space checks
# =========================================================

def _find_skinning_target(session, server):
    room = session.current_room
    if not room:
        return None, "You don't see anything to skin."
    dead = server.creatures.get_dead_creatures_in_room(room.id)
    if not dead:
        return None, "You don't see anything to skin."
    creature = dead[0]
    if creature.skinned:
        return None, f"The {creature.name} has already been skinned."
    if not creature.skin:
        return None, f"You can't skin {creature.full_name}."
    return creature, None


def _find_worn_skinning_sheath(session):
    for cont in _get_worn_containers(session):
        if _is_skinning_sheath(cont):
            return cont
    return None


def _autoskin_item_name(item):
    return str(
        item.get("short_name")
        or item.get("name")
        or item.get("noun")
        or "something"
    ).strip()


def _autoskin_container_name(container):
    return str(
        container.get("short_name")
        or container.get("name")
        or container.get("noun")
        or "container"
    ).strip()


def _autoskin_hand_for_item(session, item):
    if getattr(session, "right_hand", None) is item:
        return "right"
    if getattr(session, "left_hand", None) is item:
        return "left"
    return None


def _autoskin_container_for_item(session, item):
    cont_id = item.get("container_id")
    if cont_id is None:
        return None
    for cont in _get_worn_containers(session):
        if cont.get("inv_id") == cont_id:
            return cont
    return None


def _autoskin_ordinal(n: int) -> str:
    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _autoskin_item_ref_in_hands(session, item):
    base_name = _autoskin_item_name(item)
    matches = []
    for hand_name in ("right_hand", "left_hand"):
        held = getattr(session, hand_name, None)
        if held and _match_target(held, base_name):
            matches.append(held)
    if item not in matches:
        return base_name
    idx = matches.index(item) + 1
    if idx == 1:
        return base_name
    return f"{_autoskin_ordinal(idx)} {base_name}"


def _autoskin_item_ref_in_container(session, container, item):
    base_name = _autoskin_item_name(item)
    matches = []
    for candidate in _get_container_contents(session, container):
        if _match_target(candidate, base_name):
            matches.append(candidate)
    for candidate in container.get("contents", []):
        if _match_target(candidate, base_name):
            matches.append(candidate)
    if item not in matches:
        return base_name
    idx = matches.index(item) + 1
    if idx == 1:
        return base_name
    return f"{_autoskin_ordinal(idx)} {base_name}"


async def _autoskin_open_container_if_needed(session, server, container):
    if not container or container.get("opened"):
        return True
    await cmd_open(session, "open", _autoskin_container_name(container), server)
    return bool(container.get("opened"))


async def _autoskin_draw_item(session, server, item, container=None):
    if _autoskin_hand_for_item(session, item):
        return True
    if container:
        if not await _autoskin_open_container_if_needed(session, server, container):
            return False
        item_ref = _autoskin_item_ref_in_container(session, container, item)
        await cmd_get(
            session,
            "get",
            f"{item_ref} from {_autoskin_container_name(container)}",
            server,
        )
    else:
        await cmd_get(session, "get", _autoskin_item_name(item), server)
    return _autoskin_hand_for_item(session, item) is not None


async def _autoskin_put_held_item(session, server, item, container):
    if not container:
        return False
    if _autoskin_hand_for_item(session, item) is None:
        return False
    if not await _autoskin_open_container_if_needed(session, server, container):
        return False
    item_ref = _autoskin_item_ref_in_hands(session, item)
    await cmd_put(
        session,
        "put",
        f"{item_ref} in {_autoskin_container_name(container)}",
        server,
    )
    return item.get("container_id") == container.get("inv_id")


def _find_best_accessible_skinning_tool(session, server):
    sheath = _find_worn_skinning_sheath(session)
    if sheath:
        tool, _ = find_best_skinning_tool(_get_container_contents(session, sheath), server)
        if tool:
            return tool, sheath, "sheath"

    hand_candidates = [
        item for item in (getattr(session, "right_hand", None), getattr(session, "left_hand", None))
        if item and is_skinning_tool(item, server)
    ]
    tool, _ = find_best_skinning_tool(hand_candidates, server)
    if tool:
        return tool, None, "hand"

    other_candidates = [
        item for item in session.inventory
        if item.get("container_id") or (not item.get("slot") and not item.get("container_id"))
    ]
    tool, _ = find_best_skinning_tool(other_candidates, server)
    if tool:
        return tool, _autoskin_container_for_item(session, tool), "inventory"

    return None, None, None


async def _stash_hands_for_skinning(session, server):
    stashed = []
    for hand in ("right", "left"):
        held = session.right_hand if hand == "right" else session.left_hand
        if not held:
            continue
        best_cont = _find_best_stow_container(session, server, held, allow_special_sheath=False)
        if not best_cont:
            return False, stashed, "You need room in a pack or cloak to free your hands first."
        expected_container_id = best_cont.get("inv_id")
        item_ref = _autoskin_item_ref_in_hands(session, held)
        await cmd_stow(session, "stow", item_ref, server)
        if _autoskin_hand_for_item(session, held) is not None or held.get("container_id") != expected_container_id:
            return False, stashed, "You need room in a pack or cloak to free your hands first."
        stashed.append({"item": held, "hand": hand, "container": best_cont})
    return True, stashed, None


async def _restore_stashed_hands(session, server, stashed):
    right_row = next((row for row in stashed if row.get("hand") == "right"), None)
    left_row = next((row for row in stashed if row.get("hand") == "left"), None)

    if right_row:
        item = right_row.get("item")
        container = right_row.get("container")
        if item and _autoskin_hand_for_item(session, item) != "right":
            await _autoskin_draw_item(session, server, item, container)
        if item and _autoskin_hand_for_item(session, item) != "right":
            return False

    if left_row:
        item = left_row.get("item")
        container = left_row.get("container")
        if item and _autoskin_hand_for_item(session, item) != "left":
            await _autoskin_draw_item(session, server, item, container)
            if _autoskin_hand_for_item(session, item) != "left" and session.left_hand is None:
                await cmd_swap(session, "swap", "", server)
        if item and _autoskin_hand_for_item(session, item) != "left":
            return False

    if not right_row and left_row:
        item = left_row.get("item")
        if item and _autoskin_hand_for_item(session, item) == "right" and session.left_hand is None:
            await cmd_swap(session, "swap", "", server)
        if item and _autoskin_hand_for_item(session, item) != "left":
            return False

    return True


async def _return_tool_after_skinning(session, server, tool, tool_stash_row, source_container):
    if _autoskin_hand_for_item(session, tool) is None:
        return True

    if tool_stash_row:
        return await _autoskin_put_held_item(session, server, tool, tool_stash_row.get("container"))

    sheath = _find_worn_skinning_sheath(session)
    if sheath and await _autoskin_put_held_item(session, server, tool, sheath):
        return True

    if source_container and await _autoskin_put_held_item(session, server, tool, source_container):
        return True

    item_ref = _autoskin_item_ref_in_hands(session, tool)
    await cmd_stow(session, "stow", item_ref, server)
    return _autoskin_hand_for_item(session, tool) is None


async def _perform_skin_attempt(session, creature, server, *, allow_result_hands=True):
    room = session.current_room

    outcome = resolve_skinning(session, creature, server)
    creature.skinned = True

    tool = outcome.get("tool")
    tool_text = ""
    if tool:
        tool_name = tool.get("short_name") or tool.get("name") or tool.get("noun")
        if tool_name:
            tool_text = f" with your {tool_name}"

    if outcome.get("success"):
        skin_data = dict(outcome.get("item") or {})
        spec = outcome.get("spec") or {}

        if server.db:
            item_id = server.db.get_or_create_item(
                name=skin_data.get("name", creature.skin),
                short_name=skin_data.get("short_name", skin_data.get("name", creature.skin)),
                noun=skin_data.get("noun", (creature.skin or "skin").split()[-1]),
                item_type="skin",
                value=skin_data.get("base_value", skin_data.get("value", 1)),
                description=skin_data.get("description", f"The skin of {creature.full_name}."),
            )
            skin_data["item_id"] = item_id

        success, location, _ = auto_stow_item(
            session,
            server,
            skin_data,
            allow_hands=allow_result_hands,
        )
        display_name = skin_data.get("name") or creature.skin

        if success:
            if server.db and skin_data.get("inv_id"):
                server.db.save_item_extra_data(skin_data["inv_id"], {
                    "value": skin_data.get("value", 0),
                    "base_value": skin_data.get("base_value", 0),
                    "skin_quality": skin_data.get("skin_quality"),
                    "quality_label": skin_data.get("quality_label"),
                    "base_skin_name": skin_data.get("base_skin_name", spec.get("name")),
                })
            await session.send_line(
                f"You skin {creature.full_name}{tool_text} and obtain "
                f"{fmt_item_name(display_name)}, placing it in your {location}."
            )
            await server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} skins {creature.full_name}{tool_text} and obtains {display_name}, placing it in their {location}.",
                exclude=session,
            )
        else:
            if hasattr(server, "world"):
                server.world.add_ground_item(
                    room.id,
                    skin_data,
                    dropped_by_character_id=session.character_id,
                    dropped_by_name=session.character_name,
                    source="skin",
                )
            else:
                if not hasattr(room, "_ground_items"):
                    room._ground_items = []
                room._ground_items.append(skin_data)
            await session.send_line(
                f"You skin {creature.full_name}{tool_text} and obtain {fmt_item_name(display_name)}."
            )
            await session.send_line(colorize(
                f"No space remaining! {display_name} was left on the ground.",
                TextPresets.WARNING
            ))
            await server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} skins {creature.full_name}{tool_text} and obtains {display_name}, leaving it on the ground.",
                exclude=session,
            )

        if getattr(server, "guild", None):
            try:
                await server.guild.record_bounty_skin(session, skin_data)
            except Exception:
                pass
    else:
        if outcome.get("destroyed"):
            await session.send_line(
                f"You make a ruinous mess of {creature.full_name}{tool_text}, destroying anything of value."
            )
            await server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} makes a ruinous mess of {creature.full_name}{tool_text}, destroying anything of value.",
                exclude=session,
            )
        else:
            await session.send_line(
                f"You fail to skin {creature.full_name}{tool_text} cleanly."
            )
            await server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} fails to skin {creature.full_name}{tool_text} cleanly.",
                exclude=session,
            )

    if can_remove_corpse(creature):
        server.creatures.remove_creature(creature)

    roundtime = 4
    try:
        skin_cfg = getattr(server, "lua", None).get_skinning() if getattr(server, "lua", None) else {}
        roundtime = int(((skin_cfg or {}).get("settings") or {}).get("roundtime_seconds", 4) or 4)
    except Exception:
        roundtime = 4

    session.set_roundtime(roundtime)
    await session.send_line(roundtime_msg(roundtime))


async def cmd_skin(session, cmd, args, server):
    """SKIN - Skin a dead creature for materials. Auto-stows to inventory."""
    creature, err = _find_skinning_target(session, server)
    if not creature:
        await session.send_line(err)
        return
    await _perform_skin_attempt(session, creature, server, allow_result_hands=True)


async def cmd_autoskin(session, cmd, args, server):
    """AUTOSKIN - Execute the visible inventory-and-skin workflow for the client button."""
    creature, err = _find_skinning_target(session, server)
    if not creature:
        await session.send_line(err)
        return

    stashed = []
    ok, stashed, err = await _stash_hands_for_skinning(session, server)
    if not ok:
        await _restore_stashed_hands(session, server, stashed)
        await session.send_line(err or "You need free hands to skin that.")
        return

    tool, source_container, _source = _find_best_accessible_skinning_tool(session, server)
    if not tool:
        await _restore_stashed_hands(session, server, stashed)
        await session.send_line("You need a skinning tool before you can do that.")
        return

    tool_stash_row = next((row for row in stashed if row.get("item") is tool), None)
    if not await _autoskin_draw_item(session, server, tool, source_container):
        await _restore_stashed_hands(session, server, stashed)
        await session.send_line("You can't get your skinning tool into hand right now.")
        return

    await _perform_skin_attempt(session, creature, server, allow_result_hands=False)
    if not await _return_tool_after_skinning(session, server, tool, tool_stash_row, source_container):
        await session.send_line("You can't get your skinning tool put away properly right now.")
        return
    if not await _restore_stashed_hands(session, server, stashed):
        await session.send_line("You can't get your original hand items restored properly right now.")
# =========================================================
# AIM - Persistent body location targeting preference
# =========================================================

# Canonical location aliases a player might type (mapped to canonical key)
_AIM_ALIASES = {
    "r arm":    "right arm",   "l arm":   "left arm",
    "r hand":   "right hand",  "l hand":  "left hand",
    "r leg":    "right leg",   "l leg":   "left leg",
    "r eye":    "right eye",   "l eye":   "left eye",
    "r flank":  "right flank", "l flank": "left flank",
    "r foreleg":"right foreleg","l foreleg":"left foreleg",
    "r hindleg":"right hindleg","l hindleg":"left hindleg",
    "r wing":   "right wing",  "l wing":  "left wing",
    "r talon":  "right talon", "l talon": "left talon",
    "stomach":  "abdomen",     "belly":   "abdomen",
    "eye":      "right eye",   "arm":     "right arm",
    "leg":      "right leg",   "hand":    "right hand",
    "wing":     "right wing",  "flank":   "right flank",
}


async def cmd_aim(session, cmd, args, server):
    """AIM [location|clear|random|list] â€” Set a persistent aimed location preference.

    GS4 wiki (AIM verb):
      AIM HEAD           -- Every attack goes for the head
      AIM CLEAR / RANDOM -- Return to random hit location
      AIM LIST           -- Show valid locations

    The preference persists until changed or cleared, even between logins.
    On each attack an aim-success roll is made (d100 + CM/2 + Stalking/4 vs
    aim_penalty + creature level * 2). On failure the shot drifts to a random
    location adjacent to the aimed spot (not necessarily the aimed one).

    There is no roundtime on AIM â€” it is a preference command, not an action.
    """
    arg = (args or "").strip().lower()

    # â”€â”€ AIM LIST â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if arg in ("list", ""):
        # Show the universal list (biped) â€” we can't know target body type here
        biped_aimable = get_aimable("biped")
        lines = ["Areas at which you may AIM:"]
        # Format in two columns like GS4
        row = []
        for loc in biped_aimable:
            row.append(loc.upper().ljust(16))
            if len(row) == 2:
                lines.append("  " + "".join(row).rstrip())
                row = []
        if row:
            lines.append("  " + "".join(row).rstrip())
        lines.append("  CLEAR / RANDOM  (stop aiming)")
        lines.append("")
        lines.append(colorize(
            "Note: Valid locations depend on the creature's body type. "
            "Some locations may not apply to all creatures.",
            TextPresets.SYSTEM
        ))
        if session.aimed_location:
            lines.append(colorize(
                f"You are currently aiming at the {session.aimed_location}.",
                TextPresets.SYSTEM
            ))
        else:
            lines.append(colorize(
                "You are currently not aiming at anything in particular.",
                TextPresets.SYSTEM
            ))
        for line in lines:
            await session.send_line(line)
        return

    # â”€â”€ AIM CLEAR / RANDOM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if arg in ("clear", "random", "none", "off"):
        session.aimed_location = None
        # Persist immediately
        if server.db and session.character_id:
            server.db.save_character(session)
        await session.send_line(colorize(
            "You're now no longer aiming at anything in particular.",
            TextPresets.SYSTEM
        ))
        return

    # â”€â”€ AIM <location> â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Resolve aliases first
    canonical = _AIM_ALIASES.get(arg, arg)

    # Validate against biped as a universal baseline
    # (body-type-specific validation happens at attack time)
    resolved = resolve_aim("biped", canonical)

    # If it's not on biped, try other body types â€” player might be pre-setting
    # for an ophidian or quadruped fight
    if not resolved:
        for bt in ("quadruped", "ophidian", "hybrid", "avian", "arachnid", "insectoid"):
            resolved = resolve_aim(bt, canonical)
            if resolved:
                break

    if not resolved:
        await session.send_line(
            f"'{args.strip()}' is not a valid aim location.  "
            f"Type AIM LIST to see valid options."
        )
        return

    session.aimed_location = resolved

    # Persist immediately â€” AIM preference must survive login
    if server.db and session.character_id:
        server.db.save_character(session)

    await session.send_line(colorize(
        f"You're now aiming at the {resolved} of your target on each attack.",
        TextPresets.SYSTEM
    ))


# =========================================================
# FEINT
# =========================================================

async def cmd_feint(session, cmd, args, server):
    """FEINT <target> â€” Temporarily halves a creature's DS on your next attack.
    GS4: Uses Combat Maneuvers skill. Costs 3s RT. Debuff lasts 15 seconds.
    """
    if not args:
        if session.target and not session.target.is_dead:
            creature = session.target
        else:
            await session.send_line("Feint at what?")
            return
    else:
        creature = server.creatures.find_creature_in_room(
            args.strip().lower(),
            session.current_room.id if session.current_room else 0
        )
        if not creature or not creature.alive:
            await session.send_line(f"You don't see any '{args.strip()}' here.")
            return

    # CM skill check â€” needs at least some training
    cm_ranks = session.skills.get(4, {}).get("ranks", 0)  # SKILL_COMBAT_MANEUVERS = 4
    if cm_ranks < 1:
        await session.send_line("You lack the Combat Maneuvers training to execute a feint.")
        return

    # Success roll â€” d100 + CM bonus vs creature level * 5
    import random, time
    cm_bonus  = session.skills.get(4, {}).get("bonus", cm_ranks * 3)
    threshold = creature.level * 5
    roll      = random.randint(1, 100) + cm_bonus
    creature_display = creature.full_name

    if roll > threshold:
        # Success â€” debuff creature DS for 15 seconds
        creature._feint_until = time.time() + 15.0
        await session.send_line(
            colorize(
                f"You feint skillfully at {creature_display}, throwing it off balance!",
                TextPresets.COMBAT_HIT
            )
        )
        await session.send_line(
            colorize(
                f"  {creature_display.capitalize()} is momentarily confused â€” its defenses are lowered!",
                TextPresets.SYSTEM
            )
        )
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} feints at {creature_display}, throwing it off balance!",
            exclude=session
        )
    else:
        await session.send_line(
            f"You attempt to feint at {creature_display} but it sees through your ruse!"
        )

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_ambush(session, cmd, args, server):
    """AMBUSH [target] [location] - Attack from hiding with aimed strike."""
    _status = getattr(server, "status", None)
    if _status and _status.has(session, "stunned"):
        await session.send_line("You are stunned!  Try STUNMAN ATTACK if you have the training for it.")
        return
    if not session.hidden:
        await session.send_line("You need to be hidden first!  Try HIDE.")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    raw_args = (args or "").strip()
    aimed_location = None
    creature = None

    if not raw_args:
        creature = _resolve_combat_target(session, server, None)
        if not creature:
            await session.send_line("Ambush what?")
            return
    else:
        words = raw_args.split()
        for idx in range(len(words), 0, -1):
            candidate_name = " ".join(words[:idx])
            creature = _resolve_combat_target(session, server, candidate_name)
            if creature:
                remainder = " ".join(words[idx:]).strip()
                aimed_location = remainder or None
                break

        if not creature and session.target and not session.target.is_dead:
            creature = session.target
            aimed_location = raw_args

        if not creature:
            await session.send_line(f"You don't see any '{raw_args}' here.")
            return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    session.hidden = False
    session.sneaking = False

    await session.send_line(colorize(
        f"You emerge from hiding and ambush {creature.full_name}!",
        TextPresets.COMBAT_HIT
    ))
    await server.world.broadcast_to_room(
        session.current_room.id,
        f"{session.character_name} emerges from hiding and ambushes {creature.full_name}!",
        exclude=session
    )
    await server.combat.player_attacks_creature(
        session, creature,
        aimed_location=aimed_location,
        is_ambush=True
    )
    if getattr(server, "guild", None):
        await server.guild.record_event(session, "ambush_success")


async def cmd_ready(session, cmd, args, server):
    """READY <ammo> - Prepare ammunition for FIRE."""
    weapon, _ = _get_missile_weapon(session)
    ammo_hint = (args or "").strip()
    expected_type = _expected_ammo_type(weapon) if weapon else ""

    def _ammo_pred(item):
        return item.get("item_type") == "ammo"

    ammo, _hand_name = _find_inventory_item(session, predicate=_ammo_pred, needle=ammo_hint)
    if not ammo and expected_type:
        ammo = _find_ready_ammo(session, expected_type)
    if not ammo:
        await session.send_line("You do not have any ammunition like that available.")
        return

    ammo_type = str(ammo.get("ammo_type", "") or "")
    if expected_type and ammo_type and ammo_type != expected_type:
        await session.send_line(f"Your current weapon requires {expected_type}s, not {ammo_type}s.")
        return

    session.ready_ammo_inv_id = ammo.get("inv_id")
    session.ready_ammo_type = ammo_type
    session.ready_ammo_name = ammo.get("short_name") or ammo.get("name") or ammo_type
    await session.send_line(f"You ready {fmt_item_name(session.ready_ammo_name)} for use.")


async def cmd_fire(session, cmd, args, server):
    """FIRE <target> - Launch a ranged attack with readied ammunition."""
    weapon, _weapon_hand = _get_missile_weapon(session)
    if not weapon or (weapon.get("weapon_category", "") or "").lower() != "ranged":
        await session.send_line("You need to be holding a bow or crossbow to FIRE.")
        return
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    creature = _resolve_combat_target(session, server, (args or "").strip())
    if not creature:
        await session.send_line("Fire at what?")
        return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    ammo_type = _expected_ammo_type(weapon)
    ammo = _find_ready_ammo(session, ammo_type)
    if not ammo:
        await session.send_line(f"You need to READY some {ammo_type}s first.")
        return

    _consume_stack_item(session, ammo, 1, server)
    still_have_ready = any(row.get("inv_id") == ammo.get("inv_id") for row in (session.inventory or []))
    if getattr(session, "ready_ammo_inv_id", None) == ammo.get("inv_id") and not still_have_ready:
        session.ready_ammo_inv_id = None
        session.ready_ammo_type = None
        session.ready_ammo_name = None

    if getattr(session, "hidden", False):
        session.hidden = False
        session.sneaking = False

    await _perform_missile_attack(
        session, creature, weapon, server,
        verb="fire",
        skill_id=SKILL_RANGED,
        ds_attr="ds_ranged",
        aimed_location=getattr(session, "aimed_location", None),
    )


async def cmd_hurl(session, cmd, args, server):
    """HURL <target> - Throw a hurled weapon or throwable item."""
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    target_name = (args or "").strip()
    if not target_name:
        await session.send_line("Hurl what at whom?")
        return

    creature = _resolve_combat_target(session, server, target_name)
    if not creature:
        await session.send_line(f"You don't see any '{target_name}' here.")
        return
    if creature.is_dead:
        await session.send_line(f"The {creature.name} is already dead.")
        return

    thrown_item = None
    thrown_hand = None
    for hand_name in ("right_hand", "left_hand"):
        item = getattr(session, hand_name, None)
        if not item:
            continue
        item_type = item.get("item_type")
        category = (item.get("weapon_category", "") or "").lower()
        ammo_type = (item.get("ammo_type", "") or "").lower()
        if category == "thrown" or (item_type == "ammo" and ammo_type == "thrown"):
            thrown_item = item
            thrown_hand = hand_name
            break

    if not thrown_item:
        thrown_item = _find_ready_ammo(session, "thrown")
    if not thrown_item:
        await session.send_line("You need a throwable weapon or item to HURL.")
        return

    if thrown_item.get("item_type") == "ammo":
        _consume_stack_item(session, thrown_item, 1, server)
    else:
        _consume_item_instance(session, thrown_item, thrown_hand, server)

    if getattr(session, "hidden", False):
        session.hidden = False
        session.sneaking = False

    await _perform_missile_attack(
        session, creature, thrown_item, server,
        verb="hurl",
        skill_id=SKILL_THROWN,
        ds_attr="ds_ranged",
        aimed_location=getattr(session, "aimed_location", None),
    )


async def cmd_mstrike(session, cmd, args, server):
    """MSTRIKE [target] - Simple multi-opponent combat pass."""
    if session.position != "standing":
        await session.send_line("You need to stand up first!")
        return

    moc_ranks = _skill_ranks(session, SKILL_MOC)
    if moc_ranks <= 0:
        await session.send_line("You lack the Multi Opponent Combat training to launch a multi-strike.")
        return

    room_creatures = [
        c for c in server.creatures.get_creatures_in_room(session.current_room.id)
        if getattr(c, "alive", True) and not getattr(c, "is_dead", False)
    ]
    if not room_creatures:
        await session.send_line("There is nothing here to attack.")
        return

    swings = max(2, min(5, 1 + moc_ranks // 25))
    target_name = (args or "").strip()
    if target_name:
        target = server.creatures.find_creature_in_room(session.current_room.id, target_name)
        if not target:
            await session.send_line(f"You don't see any '{target_name}' here.")
            return
        sequence = [target] * swings
    else:
        sequence = room_creatures[:swings]

    await session.send_line(colorize(
        f"You launch into a multi-opponent assault ({len(sequence)} strikes)!",
        TextPresets.COMBAT_HIT,
    ))
    for creature in sequence:
        if creature.is_dead:
            continue
        await server.combat.player_attacks_creature(session, creature)

