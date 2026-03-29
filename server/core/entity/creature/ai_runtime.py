"""
Runtime creature AI helpers.

This module turns authored creature spell/ability metadata into live behavior.
The CreatureManager remains responsible for room iteration and lifecycle, while
this module handles per-creature combat choices.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Iterable

from server.core.commands.player.actions import _find_player_pickpocket_candidates
from server.core.commands.player.spellcasting import (
    _creature_to_spell_entity,
    _get_spell_engine,
    _lookup_spell_number,
    _lua_returns,
    _player_target_entity,
)
from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)


_STATUS_ABILITY_MAP = {
    "web_immobilize": ("webbed", 20, 22, "{name} spits a tangle of webbing over {target}!"),
    "web_trap": ("webbed", 18, 20, "{name} ensnares {target} in adhesive strands!"),
    "entangle": ("rooted", 12, 18, "{name} lashes out with grasping growth at {target}!"),
    "ensnare": ("rooted", 12, 16, "{name} tangles {target} up in a sudden snare!"),
    "bog_mire": ("slowed", 14, 18, "{name} drags {target} into a sucking mire!"),
    "howl_of_dread": ("fear", 16, 24, "{name} lets out a chilling howl that rattles {target}!"),
    "fear_howl": ("fear", 18, 22, "{name} unleashes a fearsome howl that shakes {target}!"),
    "fear_aura": ("fear", 10, 18, "{name}'s baleful presence presses hard against {target}!"),
    "aura_of_dread": ("fear", 14, 20, "{name} radiates a suffocating aura of dread around {target}!"),
    "despair_aura": ("demoralized", 14, 20, "{name} floods the air around {target} with crushing despair!"),
    "cackle_fear": ("fear", 14, 18, "{name} erupts in a shrill cackle that unsettles {target}!"),
    "hobgoblin_antics": ("demoralized", 12, 18, "{name} cackles and capers wildly, throwing {target} off balance!"),
    "paralytic_saliva": ("stunned", 6, 18, "{name} splashes paralytic venom across {target}!"),
    "paralyzing_bite": ("stunned", 7, 18, "{name}'s bite floods {target} with numbing paralysis!"),
    "disease_bite": ("disease", 90, 28, "{name} lands a filthy, infectious bite on {target}!"),
    "disease_touch": ("disease", 120, 30, "{name} brushes {target} with a wasting touch!"),
    "infectious_bite": ("disease", 90, 24, "{name}'s bite carries a festering infection into {target}!"),
    "ghoul_rot_chance": ("disease", 120, 28, "{name}'s clammy touch leaves a rot-laden taint on {target}!"),
    "disease_on_hit": ("disease", 90, 24, "{name}'s foul strike leaves {target} feeling sickly!"),
    "fel_poison_bite": ("poisoned", 40, 22, "{name} injects a sickly poison into {target}!"),
    "mild_venom": ("poisoned", 25, 18, "{name}'s venom starts to burn through {target}'s veins!"),
    "venom": ("poisoned", 35, 18, "{name} delivers a venomous strike into {target}!"),
    "venom_bite": ("poisoned", 35, 18, "{name}'s bite leaves venom coursing through {target}!"),
    "venom_sting": ("poisoned", 35, 18, "{name}'s sting leaves {target} reeling from venom!"),
    "toxic_bite": ("poisoned", 45, 22, "{name}'s toxic bite leaves {target} pale and trembling!"),
    "fire_ant_acid_sting": ("poisoned", 28, 16, "{name}'s caustic sting leaves {target} burning and woozy!"),
    "cripple_maneuver": ("slowed", 16, 20, "{name} lashes out at {target}'s legs with crippling force!"),
    "constrict_maneuver": ("immobile", 10, 18, "{name} coils tightly around {target}!"),
    "kobold_pair_knockdown": ("prone", 10, 18, "{name} darts in low and topples {target}!"),
    "stomp_quake": ("prone", 9, 16, "{name} slams the ground in a shuddering stomp beneath {target}!"),
    "charge_knockdown": ("prone", 9, 16, "{name} lowers its bulk and bowls straight through {target}!"),
    "tackle": ("prone", 8, 14, "{name} drives into {target} with a tackling rush!"),
    "trip": ("prone", 8, 14, "{name} hooks low and trips {target} off balance!"),
    "antler_sweep": ("prone", 8, 16, "{name} sweeps {target} aside with a brutal antler rake!"),
    "shield_bash": ("stunned", 5, 16, "{name} slams a shield edge-first into {target}!"),
    "hamstring": ("slowed", 14, 18, "{name} opens a vicious hamstringing cut on {target}!"),
    "stare_roundtime": ("stunned", 4, 18, "{name}'s unnerving stare freezes {target} in place!"),
    "stare_maneuver": ("stunned", 5, 18, "{name} fixes {target} in a chilling, paralyzing stare!"),
    "petrify_gaze": ("rooted", 8, 22, "{name}'s petrifying gaze locks {target}'s limbs in place!"),
    "taunt": ("demoralized", 12, 18, "{name} taunts {target} mercilessly!"),
    "mind_blast": ("stunned", 6, 20, "{name} batters {target}'s mind with a sudden psychic blast!"),
    "curse_touch": ("slowed", 14, 22, "{name} brushes {target} with a draining curse!"),
    "stunning_keen": ("stunned", 5, 16, "{name} lands a stunningly precise strike on {target}!"),
    "ghoul_master_aura": ("fear", 14, 22, "{name}'s deathly aura presses in on {target}!"),
    "thunder_roar": ("fear", 12, 20, "{name} unleashes a thunderous roar that rattles {target} to the bone!"),
}

_PREDATORY_ABILITIES = {
    "pounce_maneuver": ("prone", 10, 16, "{name} pounces and drives {target} to the ground!"),
    "pounce": ("prone", 9, 16, "{name} launches a sudden pounce at {target}!"),
    "leap_maneuver": ("staggered", 10, 14, "{name} bounds in with a leaping strike at {target}!"),
    "leap_attack": ("staggered", 10, 14, "{name} springs through the air at {target}!"),
    "stealth_ambush": ("stunned", 4, 18, "{name} lunges from cover at {target}!"),
    "ambush_attack": ("stunned", 4, 18, "{name} springs a vicious ambush on {target}!"),
    "backstab": ("stunned", 3, 18, "{name} slips in close and drives a savage strike at {target}!"),
    "carry_and_drop": ("prone", 8, 16, "{name} grabs {target} in a violent rush and slams them aside!"),
}

_SELF_HEAL_ABILITIES = {
    "golem_reconstruct": (0.25, 28, "{name} draws splintered pieces back into place and reconstructs itself!"),
}

_SELF_BUFF_ABILITIES = {
    "stone_skin": (18, 0, 24, "{name}'s hide hardens into a stone-like shell."),
    "tough_hide": (20, 0, 18, "{name}'s hide bunches into a dense protective layer."),
    "toughskin": (20, 0, 20, "{name}'s skin tightens into a resilient defensive hide."),
    "armoured_hide": (20, 0, 18, "{name}'s hide flexes into a tougher defensive posture."),
    "armoured_carapace": (24, 0, 24, "{name}'s carapace clicks into a tighter armored guard."),
    "thorn_armor": (18, 6, 14, "{name} draws thorned growth tight across its body."),
    "battle_fury": (18, 14, 8, "{name} whips itself into a battle fury!"),
    "battle_rage": (18, 18, 4, "{name} flies into a violent battle rage!"),
    "chieftain_war_cry": (20, 14, 10, "{name} bellows a war cry that rallies its blood!"),
    "rally_trolls": (20, 12, 8, "{name} roars a rallying cry to its kin."),
    "intimidating_presence": (18, 8, 12, "{name} squares up with a menacing, dominant stance."),
    "war_hardened": (24, 10, 16, "{name}'s veteran instincts sharpen into a hard defensive line."),
    "krolvin_resilience": (20, 8, 14, "{name} digs in stubbornly against the fight."),
    "spell_shield_219": (22, 0, 20, "{name} gathers a shield of spell warding around itself."),
    "spirit_warding_2": (22, 0, 14, "{name} murmurs a warding prayer and steadies itself."),
    "glamour": (18, 6, 12, "{name}'s outline shimmers and slips uncertainly in your vision."),
    "evade_maneuver": (14, 0, 18, "{name} darts into an evasive weave."),
    "shadow_meld": (16, 10, 14, "{name} melts into the nearest shadows."),
    "hide": (12, 6, 10, "{name} slips into cover and vanishes from plain sight."),
    "hide_in_shadows": (14, 10, 12, "{name} fades back into the shadows."),
    "phase": (16, 0, 18, "{name} blurs and phases partly out of step with the room."),
    "phase_through_terrain": (18, 0, 20, "{name} ripples and seems half-phased into the surroundings."),
    "non_corporeal": (18, 0, 20, "{name}'s outline wavers into a ghostly, half-corporeal shape."),
    "float": (16, 0, 12, "{name} drifts lightly above the ground."),
    "pack_hunting": (16, 10, 8, "{name} circles with predatory pack intent."),
    "frenzied_attack": (14, 12, 4, "{name} whips itself into a frenzied attack pattern!"),
    "woodsman_heft": (18, 10, 8, "{name} sets its shoulders and hefts its weapon with practiced force."),
    "trackless_step": (16, 8, 12, "{name} moves with uncanny, trackless precision."),
    "puncture_resistant": (18, 0, 10, "{name}'s hide shifts to blunt piercing blows."),
    "undead_resilience": (18, 0, 12, "{name}'s dead flesh stiffens with unnatural resilience."),
    "shambling_gait": (18, 0, 10, "{name} lurches into a stubborn, shambling guard."),
}

_DIRECT_ATTACK_ABILITIES = {
    "acid_spray": {"as_bonus": 8, "damage_type": "acid", "cooldown": 16, "verb_first": "sprays sizzling acid across you", "verb_third": "sprays sizzling acid across {target}"},
    "ant_acid_spray": {"as_bonus": 6, "damage_type": "acid", "cooldown": 14, "verb_first": "sprays stinging acid across you", "verb_third": "sprays stinging acid across {target}"},
    "fire_spit": {"as_bonus": 10, "damage_type": "fire", "cooldown": 14, "verb_first": "spits fire at you", "verb_third": "spits fire at {target}"},
    "fire_bolt": {"as_bonus": 12, "damage_type": "fire", "cooldown": 16, "verb_first": "hurls a bolt of fire at you", "verb_third": "hurls a bolt of fire at {target}"},
    "water_bolt": {"as_bonus": 9, "damage_type": "crush", "cooldown": 14, "verb_first": "lashes you with a bolt of water", "verb_third": "lashes {target} with a bolt of water"},
    "call_wind": {"as_bonus": 10, "damage_type": "crush", "cooldown": 18, "verb_first": "whips a violent gust into you", "verb_third": "whips a violent gust into {target}"},
    "flame_burst": {"as_bonus": 12, "damage_type": "fire", "cooldown": 16, "verb_first": "erupts in a burst of flame against you", "verb_third": "erupts in a burst of flame against {target}"},
    "heat_wave": {"as_bonus": 12, "damage_type": "fire", "cooldown": 18, "verb_first": "rolls a punishing heat wave into you", "verb_third": "rolls a punishing heat wave into {target}"},
    "cold_flare": {"as_bonus": 9, "damage_type": "cold", "cooldown": 14, "verb_first": "lashes you with a burst of killing frost", "verb_third": "lashes {target} with a burst of killing frost"},
    "cold_aura": {"as_bonus": 8, "damage_type": "cold", "cooldown": 14, "verb_first": "freezes the air around you", "verb_third": "freezes the air around {target}"},
    "heat_aura": {"as_bonus": 8, "damage_type": "fire", "cooldown": 14, "verb_first": "sears you with a wave of heat", "verb_third": "sears {target} with a wave of heat"},
    "flame_aura": {"as_bonus": 8, "damage_type": "fire", "cooldown": 14, "verb_first": "lashes you with flaring heat", "verb_third": "lashes {target} with flaring heat"},
    "chill_touch": {"as_bonus": 8, "damage_type": "cold", "cooldown": 14, "verb_first": "lays a freezing touch on you", "verb_third": "lays a freezing touch on {target}"},
    "fire_touch": {"as_bonus": 8, "damage_type": "fire", "cooldown": 14, "verb_first": "brands you with a burning touch", "verb_third": "brands {target} with a burning touch"},
    "freeze_bite": {"as_bonus": 12, "damage_type": "cold", "cooldown": 16, "verb_first": "sinks a freezing bite into you", "verb_third": "sinks a freezing bite into {target}"},
    "tail_spike_volley": {"as_bonus": 10, "damage_type": "puncture", "cooldown": 16, "verb_first": "fans a spike volley into you", "verb_third": "fans a spike volley into {target}"},
    "tail_strike": {"as_bonus": 9, "damage_type": "crush", "cooldown": 14, "verb_first": "lashes you with a snapping tail strike", "verb_third": "lashes {target} with a snapping tail strike"},
    "tail_sweep": {"as_bonus": 10, "damage_type": "crush", "cooldown": 14, "verb_first": "sweeps a heavy tail into your legs", "verb_third": "sweeps a heavy tail into {target}"},
    "bear_maul": {"as_bonus": 12, "damage_type": "slash", "cooldown": 16, "verb_first": "mauls you with a savage rush", "verb_third": "mauls {target} with a savage rush"},
    "powerful_blow": {"as_bonus": 12, "damage_type": "crush", "cooldown": 14, "verb_first": "lands a crushing blow on you", "verb_third": "lands a crushing blow on {target}"},
    "powerful_kick": {"as_bonus": 10, "damage_type": "crush", "cooldown": 14, "verb_first": "drives a brutal kick into you", "verb_third": "drives a brutal kick into {target}"},
    "powerful_gore": {"as_bonus": 12, "damage_type": "puncture", "cooldown": 16, "verb_first": "gores you with tremendous force", "verb_third": "gores {target} with tremendous force"},
    "aimed_shot": {"as_bonus": 12, "damage_type": "puncture", "cooldown": 16, "verb_first": "looses a carefully aimed shot at you", "verb_third": "looses a carefully aimed shot at {target}"},
    "sonic_wail": {"as_bonus": 10, "damage_type": "crush", "cooldown": 18, "verb_first": "shreds you with a sonic wail", "verb_third": "shreds {target} with a sonic wail", "status": "stunned", "duration": 4},
    "mind_blast": {"as_bonus": 10, "damage_type": "crush", "cooldown": 18, "verb_first": "hammers your mind with psychic force", "verb_third": "hammers {target}'s mind with psychic force", "status": "stunned", "duration": 4},
    "spirit_strike": {"as_bonus": 10, "damage_type": "crush", "cooldown": 16, "verb_first": "lashes you with spiritual force", "verb_third": "lashes {target} with spiritual force"},
    "life_drain": {"as_bonus": 12, "damage_type": "crush", "cooldown": 18, "verb_first": "draws the life out of you", "verb_third": "draws the life out of {target}", "self_heal_frac": 0.18},
    "life_leech": {"as_bonus": 12, "damage_type": "crush", "cooldown": 18, "verb_first": "leeches vitality from you", "verb_third": "leeches vitality from {target}", "self_heal_frac": 0.16},
    "wight_drain": {"as_bonus": 12, "damage_type": "cold", "cooldown": 18, "verb_first": "drains the warmth from your body", "verb_third": "drains the warmth from {target}'s body", "self_heal_frac": 0.14},
    "spirit_drain": {"as_bonus": 10, "damage_type": "crush", "cooldown": 18, "verb_first": "drains your spirit with a clutching touch", "verb_third": "drains {target}'s spirit with a clutching touch", "self_heal_frac": 0.14},
    "soul_drain": {"as_bonus": 12, "damage_type": "crush", "cooldown": 18, "verb_first": "tears at your soul with chilling force", "verb_third": "tears at {target}'s soul with chilling force", "self_heal_frac": 0.18},
    "gas_cloud": {"as_bonus": 8, "damage_type": "crush", "cooldown": 18, "verb_first": "engulfs you in a choking gas cloud", "verb_third": "engulfs {target} in a choking gas cloud", "status": "poisoned", "duration": 8},
    "tremors": {"as_bonus": 8, "damage_type": "crush", "cooldown": 18, "verb_first": "bucks the ground violently beneath you", "verb_third": "bucks the ground violently beneath {target}", "status": "prone", "duration": 4},
    "earthen_fury_caster": {"as_bonus": 12, "damage_type": "crush", "cooldown": 18, "verb_first": "hammers you with earthen fury", "verb_third": "hammers {target} with earthen fury"},
    "sulfurous_appearance": {"as_bonus": 8, "damage_type": "fire", "cooldown": 16, "verb_first": "lashes you with a sulfurous flare", "verb_third": "lashes {target} with a sulfurous flare", "status": "fear", "duration": 4},
    "rend": {"as_bonus": 12, "damage_type": "slash", "cooldown": 16, "verb_first": "rends into you with tearing force", "verb_third": "rends into {target} with tearing force"},
    "shock_burst": {"as_bonus": 11, "damage_type": "electric", "cooldown": 16, "verb_first": "detonates a crackling burst of lightning into you", "verb_third": "detonates a crackling burst of lightning into {target}", "status": "stunned", "duration": 3},
}

_DISARM_ABILITIES = {
    "scavenge_weapon": ("snatches at {target}'s weapon with grubby opportunism!", 22),
    "disarm_weapon": ("hooks and twists, trying to rip {target}'s weapon free!", 24),
    "sunder_shield": ("slams hard against {target}'s shield arm, trying to spoil their guard!", 24),
}

_REGEN_ABILITIES = {
    "troll_regeneration": (0.07, 12, "{name}'s flesh knits together with trollish speed."),
    "lycanthrope_regeneration": (0.06, 12, "{name}'s wounds seal over beneath a surge of bestial vigor."),
    "golem_reconstruct": (0.08, 14, "{name}'s frame crackles and re-forms around its core."),
}

_SPECIAL_LOOT_BY_ABILITY = {
    "crystal_core_drop": "a crystal core",
    "essence_shard_drop": "an essence shard",
    "drops_pale_water_sapphire": "a pale water sapphire",
}


def recompute_group_modifiers(manager, creature):
    """Apply room-local pack/formation bonuses from authored ability tags."""
    abilities = {str(a or "").lower() for a in (getattr(creature, "abilities", []) or [])}
    creature.ai_as_bonus = 0
    creature.ai_ds_bonus = 0
    if not abilities:
        return

    room_creatures = [
        other for other in manager.get_creatures_in_room(creature.current_room_id)
        if other.alive and other.id != creature.id
    ]
    family_allies = [
        other for other in room_creatures
        if getattr(other, "family", "") and getattr(other, "family", "") == getattr(creature, "family", "")
    ]
    template_allies = [
        other for other in room_creatures
        if getattr(other, "template_id", "") == getattr(creature, "template_id", "")
    ]

    if "pack_tactics" in abilities or "pack_hunting" in abilities:
        pack_count = len(family_allies)
        creature.ai_as_bonus += min(20, pack_count * 6)
        creature.ai_ds_bonus += min(16, pack_count * 4)

    if "formation_fighting" in abilities:
        formation_count = len(template_allies)
        creature.ai_as_bonus += min(18, formation_count * 5)
        creature.ai_ds_bonus += min(20, formation_count * 5)


async def attempt_special_action(manager, creature, target, now: float) -> bool:
    """Try a spell or special ability before a normal melee swing."""
    apply_passive_behavior(manager, creature, now)
    abilities = [str(a or "").lower() for a in (getattr(creature, "abilities", []) or []) if str(a or "").strip()]

    if getattr(creature, "spells", None) and creature.can_cast_spell(now):
        if await _attempt_spellcast(manager, creature, target):
            return True

    for ability in abilities:
        if not creature.can_use_ability(ability, now):
            continue
        if ability in _SELF_BUFF_ABILITIES:
            if await _attempt_self_buff(manager, creature, ability):
                return True
        if ability in _SELF_HEAL_ABILITIES:
            if await _attempt_self_heal(manager, creature, ability):
                return True
        if ability in _DIRECT_ATTACK_ABILITIES:
            if await _attempt_direct_attack(manager, creature, target, ability):
                return True
        if ability in {"hurl_weapon", "stone_throw"}:
            if await _attempt_ranged_attack(manager, creature, target, ability):
                return True
        if ability in _PREDATORY_ABILITIES:
            if await _attempt_predatory_strike(manager, creature, target, ability):
                return True
        if ability in _DISARM_ABILITIES:
            if await _attempt_disarm(manager, creature, target, ability):
                return True
        if ability in {"steal_item", "pickpocket_attempt"}:
            if await _attempt_theft(manager, creature, target, ability):
                return True
        if ability in _STATUS_ABILITY_MAP:
            if await _attempt_status_ability(manager, creature, target, ability):
                return True
    return False


def apply_passive_behavior(manager, creature, now: float):
    abilities = {str(a or "").lower() for a in (getattr(creature, "abilities", []) or [])}
    creature.prune_temporary_effects(now)
    immune = {str(x or "").lower() for x in (getattr(creature, "immune", []) or [])}
    for ability_id, immunity in {
        "cold_immune": "cold",
        "cold_immunity": "cold",
        "fire_immune": "fire",
        "blindness_immunity": "blindness",
        "holding_song_immune": "holding_song",
    }.items():
        if ability_id in abilities and immunity not in immune:
            creature.immune.append(immunity)
            immune.add(immunity)

    # Some authored loot tags are ability-based rather than explicit special_loot.
    for ability_id, item_name in _SPECIAL_LOOT_BY_ABILITY.items():
        if ability_id in abilities and item_name not in creature.special_loot:
            creature.special_loot.append(item_name)

    if "rapid_decay" in abilities and int(getattr(creature, "decay_seconds", 300) or 300) > 120:
        creature.decay_seconds = 120

    for ability_id, (heal_frac, cooldown, line) in _REGEN_ABILITIES.items():
        if ability_id not in abilities:
            continue
        if int(getattr(creature, "health_current", 0) or 0) >= int(getattr(creature, "health_max", 1) or 1):
            continue
        if not creature.can_use_ability(f"passive:{ability_id}", now):
            continue
        heal_amount = max(1, int((getattr(creature, "health_max", 1) or 1) * float(heal_frac or 0.05)))
        creature.heal(heal_amount)
        creature.set_ability_cooldown(f"passive:{ability_id}", cooldown)
        try:
            asyncio.create_task(
                manager.server.world.broadcast_to_room(
                    creature.current_room_id,
                    colorize(line.format(name=creature.full_name.capitalize()), TextPresets.CREATURE_NAME),
                )
            )
        except Exception:
            pass

    if "gremlin_eat_grub" in abilities and int(getattr(creature, "health_current", 0) or 0) < int(getattr(creature, "health_max", 1) or 1):
        if creature.can_use_ability("passive:gremlin_eat_grub", now):
            creature.heal(max(1, int((getattr(creature, "health_max", 1) or 1) * 0.05)))
            creature.set_ability_cooldown("passive:gremlin_eat_grub", 16)

    if "burrowing_escape" in abilities and float(getattr(creature, "health_current", 0) or 0) / max(1.0, float(getattr(creature, "health_max", 1) or 1)) <= 0.35:
        if not creature.has_temporary_state("burrowing_escape", now):
            creature.apply_temporary_state("burrowing_escape", 12)
            creature.apply_temporary_bonus("burrowing_escape", 12, ds_bonus=16)
    if "wall_climb" in abilities or "swim" in abilities:
        creature.apply_temporary_state("terrain_mobile", 12)


def sniff_bonus(creature) -> int:
    abilities = {str(a or "").lower() for a in (getattr(creature, "abilities", []) or [])}
    bonus = 0
    if "cave_sight" in abilities or "tunnel_sight" in abilities:
        bonus += 12
    if "scouting_awareness" in abilities:
        bonus += 14
    if "trackless_step" in abilities:
        bonus += 6
    if "pack_hunting" in abilities:
        bonus += 8
    return bonus


async def _attempt_self_heal(manager, creature, ability_id: str) -> bool:
    frac, cooldown, line = _SELF_HEAL_ABILITIES[ability_id]
    if int(getattr(creature, "health_current", 0) or 0) >= int((getattr(creature, "health_max", 1) or 1) * 0.6):
        return False
    heal_amount = max(1, int((getattr(creature, "health_max", 1) or 1) * float(frac or 0.2)))
    creature.heal(heal_amount)
    creature.set_ability_cooldown(ability_id, cooldown)
    creature.set_roundtime(5)
    await manager.server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(line.format(name=creature.full_name.capitalize()), TextPresets.CREATURE_NAME),
    )
    return True


async def _attempt_spellcast(manager, creature, target) -> bool:
    server = manager.server
    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        return False

    entries: list = list(getattr(creature, "spells", []) or [])
    random.shuffle(entries)
    for entry in entries:
        if isinstance(entry, dict):
            spell_name = str(entry.get("name") or "").strip()
            cooldown = float(entry.get("cooldown", 10 + max(0, int(getattr(creature, "level", 1) or 1) // 2)))
        else:
            spell_name = str(entry or "").strip()
            cooldown = float(10 + max(0, int(getattr(creature, "level", 1) or 1) // 2))
        if not spell_name:
            continue
        spell_number = (
            _lookup_spell_number(server, spell_name)
            or _lookup_spell_number(server, spell_name.replace("_", " "))
        )
        if not spell_number:
            continue
        try:
            raw_char = engine.python_to_lua(_creature_to_spell_entity(creature))
            raw_target = engine.python_to_lua(_player_target_entity(target, server))
            raw = engine.call_hook(
                spell_engine,
                "cast_direct",
                raw_char,
                raw_target,
                int(spell_number),
                "cast",
                None,
                True,
            )
            values = _lua_returns(raw)
            ok = bool(values[0]) if values else False
            message = str(values[1] or "").strip() if len(values) > 1 else ""
        except Exception as e:
            log.debug("Creature spellcast failed for %s/%s: %s", creature.template_id, spell_name, e)
            continue
        if not ok:
            continue

        creature.set_spell_cooldown(cooldown)
        creature.set_roundtime(3)
        room_id = int(getattr(creature, "current_room_id", 0) or 0)
        prefix = f"{creature.full_name.capitalize()} gestures and unleashes {spell_name.replace('_', ' ')}!"
        if message:
            prefix = f"{prefix}\n  {message}"
        await server.world.broadcast_to_room(room_id, colorize(prefix, TextPresets.CREATURE_NAME))
        return True
    return False


async def _attempt_self_buff(manager, creature, ability_id: str) -> bool:
    duration, as_bonus, ds_bonus, line = _SELF_BUFF_ABILITIES[ability_id]
    if creature.has_temporary_state(ability_id):
        return False
    creature.apply_temporary_state(ability_id, duration)
    creature.apply_temporary_bonus(ability_id, duration, as_bonus=as_bonus, ds_bonus=ds_bonus)
    creature.set_ability_cooldown(ability_id, max(12, int(duration // 2)))
    creature.set_roundtime(4)
    await manager.server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(line.format(name=creature.full_name.capitalize()), TextPresets.CREATURE_NAME),
    )
    return True


async def _attempt_status_ability(manager, creature, target, ability_id: str) -> bool:
    server = manager.server
    status = getattr(server, "status", None)
    effect_id, duration, cooldown, line = _STATUS_ABILITY_MAP[ability_id]
    if status and status.has(target, effect_id):
        return False
    if random.random() > 0.55:
        return False
    if status:
        status.apply(target, effect_id, duration=duration)
    creature.set_ability_cooldown(ability_id, cooldown)
    creature.set_roundtime(5)
    await server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(line.format(name=creature.full_name.capitalize(), target=target.character_name), TextPresets.CREATURE_NAME),
    )
    return True


async def _attempt_predatory_strike(manager, creature, target, ability_id: str) -> bool:
    server = manager.server
    status = getattr(server, "status", None)
    effect_id, duration, cooldown, line = _PREDATORY_ABILITIES[ability_id]
    if random.random() > 0.55:
        return False
    if status:
        status.apply(target, effect_id, duration=duration)
    creature.force_attack_once(_predatory_attack_profile(creature, ability_id))
    creature.set_ability_cooldown(ability_id, cooldown)
    await server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(line.format(name=creature.full_name.capitalize(), target=target.character_name), TextPresets.CREATURE_NAME),
    )
    await manager._creature_attack(creature, target)
    return True


async def _attempt_direct_attack(manager, creature, target, ability_id: str) -> bool:
    config = _DIRECT_ATTACK_ABILITIES[ability_id]
    if random.random() > 0.60:
        return False
    attack = {
        "name": ability_id,
        "as": int(getattr(creature, "as_melee", 40) or 40) + int(config.get("as_bonus", 8) or 8),
        "damage_type": str(config.get("damage_type") or getattr(creature, "damage_type", "crush") or "crush"),
        "verb_first": str(config.get("verb_first") or "strikes you savagely"),
        "verb_third": str(config.get("verb_third") or "strikes {target} savagely"),
        "roundtime": int(config.get("roundtime", 5) or 5),
    }
    creature.force_attack_once(attack)
    creature.set_ability_cooldown(ability_id, float(config.get("cooldown", 14) or 14))
    if config.get("status"):
        status = getattr(manager.server, "status", None)
        if status:
            status.apply(target, str(config["status"]), duration=int(config.get("duration", 4) or 4))
    if config.get("self_heal_frac"):
        heal_amount = max(1, int((getattr(creature, "health_max", 1) or 1) * float(config["self_heal_frac"])))
        creature.heal(heal_amount)
    await manager.server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(f"{creature.full_name.capitalize()} readies a special attack!", TextPresets.CREATURE_NAME),
    )
    await manager._creature_attack(creature, target)
    return True


def _predatory_attack_profile(creature, ability_id: str) -> dict:
    verbs = {
        "pounce_maneuver": ("crashes into you with a savage pounce", "crashes into {target} with a savage pounce"),
        "pounce": ("pounces viciously at you", "pounces viciously at {target}"),
        "leap_maneuver": ("leaps at you in a blur", "leaps at {target} in a blur"),
        "stealth_ambush": ("slashes from concealment", "slashes from concealment at {target}"),
        "ambush_attack": ("ambushes you with a brutal strike", "ambushes {target} with a brutal strike"),
        "backstab": ("drives in with a vicious backstab", "drives in with a vicious backstab at {target}"),
    }
    verb_first, verb_third = verbs.get(ability_id, ("attacks you savagely", "attacks {target} savagely"))
    return {
        "name": ability_id,
        "as": int(getattr(creature, "as_melee", 40) or 40) + 14,
        "damage_type": getattr(creature, "damage_type", "slash") or "slash",
        "verb_first": verb_first,
        "verb_third": verb_third,
        "roundtime": 5,
    }


async def _attempt_ranged_attack(manager, creature, target, ability_id: str) -> bool:
    server = manager.server
    if random.random() > 0.60:
        return False
    attack = {
        "name": ability_id,
        "as": int(getattr(creature, "as_melee", 40) or 40) + 10,
        "damage_type": "crush" if ability_id == "stone_throw" else getattr(creature, "damage_type", "slash"),
        "verb_first": "hurls a missile at you" if ability_id == "stone_throw" else "hurls a weapon at you",
        "verb_third": "hurls a missile at {target}" if ability_id == "stone_throw" else "hurls a weapon at {target}",
        "roundtime": 5,
    }
    creature.force_attack_once(attack)
    creature.set_ability_cooldown(ability_id, 12)
    await server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(
            f"{creature.full_name.capitalize()} winds up and {'hurls a stone' if ability_id == 'stone_throw' else 'lets fly with a stolen weapon'} at {target.character_name}!",
            TextPresets.CREATURE_NAME,
        ),
    )
    await manager._creature_attack(creature, target)
    return True


async def _attempt_theft(manager, creature, target, ability_id: str) -> bool:
    server = manager.server
    candidates = _find_player_pickpocket_candidates(target, "")
    if not candidates or random.random() > 0.45:
        return False
    item, _source = candidates[0]
    removed = _remove_stolen_item_from_player(target, item, server)
    if not removed:
        return False
    creature.stolen_items.append(removed)
    creature.set_ability_cooldown(ability_id, 20)
    creature.set_roundtime(5)
    item_name = removed.get("short_name") or removed.get("name") or "something"
    await server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(
            f"{creature.full_name.capitalize()} snatches {item_name} from {target.character_name}!",
            TextPresets.WARNING,
        ),
    )
    if hasattr(target, "send_line"):
        await target.send_line(colorize(f"  {creature.full_name.capitalize()} steals {item_name} from you!", TextPresets.WARNING))
    return True


async def _attempt_disarm(manager, creature, target, ability_id: str) -> bool:
    if random.random() > 0.40:
        return False
    item = getattr(target, "right_hand", None) or getattr(target, "left_hand", None)
    if not item and ability_id != "sunder_shield":
        return False
    line, cooldown = _DISARM_ABILITIES[ability_id]
    creature.set_ability_cooldown(ability_id, cooldown)
    creature.set_roundtime(5)
    if ability_id == "sunder_shield":
        status = getattr(manager.server, "status", None)
        if status:
            status.apply(target, "demoralized", duration=10)
        await manager.server.world.broadcast_to_room(
            creature.current_room_id,
            colorize(line.format(name=creature.full_name.capitalize(), target=target.character_name), TextPresets.WARNING),
        )
        return True
    removed = _remove_stolen_item_from_player(target, item, manager.server)
    if not removed:
        return False
    creature.stolen_items.append(removed)
    item_name = removed.get("short_name") or removed.get("name") or "something"
    await manager.server.world.broadcast_to_room(
        creature.current_room_id,
        colorize(
            f"{creature.full_name.capitalize()} {line.format(name=creature.full_name.capitalize(), target=target.character_name)}",
            TextPresets.WARNING,
        ),
    )
    if hasattr(target, "send_line"):
        await target.send_line(colorize(f"  Your {item_name} is torn from your grip!", TextPresets.WARNING))
    return True


def _remove_stolen_item_from_player(target, item: dict, server):
    removed = dict(item or {})
    removed.pop("slot", None)
    removed["container_id"] = None
    removed.pop("inv_id", None)

    if getattr(target, "right_hand", None) is item:
        target.right_hand = None
    elif getattr(target, "left_hand", None) is item:
        target.left_hand = None
    else:
        try:
            target.inventory.remove(item)
        except Exception:
            return None

    inv_id = item.get("inv_id")
    if inv_id and getattr(server, "db", None):
        try:
            server.db.remove_item_from_inventory(inv_id)
        except Exception as e:
            log.debug("Failed to remove stolen inventory row %s: %s", inv_id, e)
    return removed


def pack_follow_candidates(manager, leader) -> Iterable:
    abilities = {str(a or "").lower() for a in (getattr(leader, "abilities", []) or [])}
    if "pack_tactics" not in abilities and "pack_hunting" not in abilities and "formation_fighting" not in abilities:
        return []
    followers = []
    for other in manager.get_creatures_in_room(leader.current_room_id):
        if other.id == leader.id or not other.alive or other.in_combat:
            continue
        other_abilities = {str(a or "").lower() for a in (getattr(other, "abilities", []) or [])}
        if "pack_tactics" in abilities or "pack_tactics" in other_abilities:
            if getattr(other, "family", "") and getattr(other, "family", "") == getattr(leader, "family", ""):
                followers.append(other)
                continue
        if "formation_fighting" in abilities or "formation_fighting" in other_abilities:
            if getattr(other, "template_id", "") == getattr(leader, "template_id", ""):
                followers.append(other)
    return followers
