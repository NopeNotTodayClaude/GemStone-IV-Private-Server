"""
CombatEngine - GemStone IV combat system with authentic GS4/Lich messaging.

Attack Roll Format (GS4 authentic):
  Player: "You swing a steel short sword at a giant ant!
           AS: +82 vs DS: +30 with AvD: +35 + d100 roll: +74 = +161
           ... and hit for 20 points of damage!"
  Creature: "A giant ant [Level 5] snaps at you with massive mandibles!
             AS: +80 vs DS: +45 with AvD: +30 + d100 roll: +63 = +128
             ... 12 hit points of damage to your chest!"

Core formula:  EndRoll = d100 + AS - DS + AvD
If EndRoll > 100, the attack hits.
Raw Damage = (EndRoll - 100) * WeaponDamageFactor
CritRank = floor(RawDamage / CritDivisor), capped at 9.

Stance modifiers:
  Offensive:  AS +20, DS -20
  Advance:    AS +15, DS -10
  Forward:    AS +10, DS  0
  Neutral:    AS  0,  DS  0
  Guarded:    AS -10, DS +15
  Defensive:  AS -20, DS +25
"""

import random
import logging
from server.core.protocol.colors import (
    colorize, TextPresets, creature_name as fmt_creature_name,
    combat_damage, combat_crit, combat_death, roundtime_msg
)
from server.core.engine.encumbrance import (
    encumbrance_as_ds_penalty, encumbrance_rt_penalty
)
from server.core.engine.magic_effects import apply_roundtime_effects, get_active_buff_totals
from server.core.scripting.loaders.body_types_loader import (
    get_locations, get_aimable, random_location, resolve_aim
)
from server.core.engine.combat.material_combat import (
    resolve_flare, get_crit_phantom, resolve_armor_flare
)
from server.core.engine.combat.status_effects import get_combat_mods
from server.core.scripting.lua_bindings.weapon_api import set_reaction_trigger
from server.core.scripting.lua_bindings.combat_maneuver_api import (
    consume_on_attack_bonuses,
    get_passive_combat_mods,
    get_temp_combat_bonus_totals,
    maybe_auto_stand_before_attack,
)

log = logging.getLogger(__name__)


def _status_combat_mods(server, entity) -> tuple[int, int, int, int, int]:
    mgr = getattr(server, "status", None)
    if mgr:
        try:
            return tuple(int(v or 0) for v in mgr.get_combat_mods(entity))
        except Exception:
            pass
    as_mod, ds_mod = get_combat_mods(entity)
    return int(as_mod or 0), int(ds_mod or 0), 0, 0, 0


def _holy_flare_damage(session, server) -> int:
    buffs = _buff_totals(session, server)
    if not buffs.get("holy_flares"):
        return 0
    if random.random() > 0.25:
        return 0
    level = int(getattr(session, "level", 1) or 1)
    return random.randint(6, 14) + max(0, level // 3)


def _apply_player_wards(server, session, hp_damage: int) -> tuple[int, list[str]]:
    damage = max(0, int(hp_damage or 0))
    notes = []
    buffs = _buff_totals(session, server)

    life_ward = int(buffs.get("life_ward", 0) or 0)
    if life_ward > 0 and damage > 0:
        absorbed = min(damage, life_ward)
        damage -= absorbed
        notes.append(f"Your life ward absorbs {absorbed} damage.")
        if getattr(server, "db", None) and getattr(session, "character_id", None):
            try:
                import json
                rows = server.db.execute_query(
                    """
                    SELECT id, effects_json
                    FROM character_active_buffs
                    WHERE character_id=%s
                      AND (expires_at IS NULL OR expires_at > NOW())
                    """,
                    (session.character_id,),
                ) or []
                remaining = max(0, life_ward - absorbed)
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    try:
                        effects = json.loads(row.get("effects_json") or "{}")
                    except Exception:
                        continue
                    if "life_ward" not in effects:
                        continue
                    if remaining > 0:
                        effects["life_ward"] = remaining
                        server.db.execute_update(
                            "UPDATE character_active_buffs SET effects_json=%s WHERE id=%s",
                            (json.dumps(effects), row.get("id")),
                        )
                    else:
                        server.db.execute_update(
                            "DELETE FROM character_active_buffs WHERE id=%s",
                            (row.get("id"),),
                        )
                    break
            except Exception:
                pass

    redirect = int(buffs.get("damage_redirect", 0) or 0)
    if redirect > 0 and damage > 0:
        redirected = min(damage, redirect)
        damage -= redirected
        notes.append(f"An empathic link diverts {redirected} damage away from you.")

    return damage, notes


# ── Skill IDs (match skills seed auto-increment) ─────────────────────────────
SKILL_TWC               = 1
SKILL_ARMOR_USE         = 2
SKILL_SHIELD_USE        = 3
SKILL_COMBAT_MANEUVERS  = 4
SKILL_EDGED_WEAPONS     = 5
SKILL_BLUNT_WEAPONS     = 6
SKILL_TWO_HANDED        = 7
SKILL_RANGED            = 8
SKILL_THROWN            = 9
SKILL_POLEARM           = 10
SKILL_BRAWLING          = 11
SKILL_MOC               = 12
SKILL_PHYSICAL_FITNESS  = 13
SKILL_DODGING           = 14


def _sr(session, skill_id):
    """Get skill ranks by integer ID, safe default 0."""
    d = (getattr(session, 'skills', {}) or {}).get(skill_id, {})
    return int(d.get('ranks', 0)) if isinstance(d, dict) else 0


def _sb(session, skill_id):
    """Get skill bonus by integer ID. Falls back to ranks*3."""
    d = (getattr(session, 'skills', {}) or {}).get(skill_id, {})
    if isinstance(d, dict):
        b = int(d.get('bonus', 0))
        return b if b else _sr(session, skill_id) * 3
    return 0


def _buff_totals(session, server):
    db = getattr(server, "db", None)
    char_id = getattr(session, "character_id", None)
    if not db or not char_id:
        return {}
    try:
        return db.get_active_buff_effect_totals(char_id) or {}
    except Exception:
        return {}


def _weapon_skill_id(weapon):
    """Map weapon_category string to its skill ID."""
    cat = (weapon.get('weapon_category', 'edged') or 'edged').lower() if weapon else 'edged'
    return {
        'edged':     SKILL_EDGED_WEAPONS,
        'blunt':     SKILL_BLUNT_WEAPONS,
        'twohanded': SKILL_TWO_HANDED,
        'polearm':   SKILL_POLEARM,
        'ranged':    SKILL_RANGED,
        'thrown':    SKILL_THROWN,
        'brawling':  SKILL_BRAWLING,
    }.get(cat, SKILL_EDGED_WEAPONS)


# Base Damage Factor for natural attacks when no weapon template DF exists.
DAMAGE_FACTORS = {
    "slash": 0.30,
    "crush": 0.25,
    "puncture": 0.35,
    "fire": 0.28,
    "cold": 0.28,
    "electrical": 0.28,
}

ARMOR_GROUP_BY_ASG = {
    1: "cloth", 2: "cloth",
    3: "leather", 4: "leather", 5: "leather", 6: "leather", 7: "leather", 8: "leather",
    9: "scale", 10: "scale", 11: "scale", 12: "scale",
    13: "chain", 14: "chain", 15: "chain", 16: "chain",
    17: "plate", 18: "plate", 19: "plate", 20: "plate",
}

# Armor-aware AvD values. Still hand-curated, but no longer a single flat number
# for every armor type wearing the same hit.
AVD_TABLE = {
    "slash":      {"cloth": 38, "leather": 34, "scale": 28, "chain": 24, "plate": 20},
    "crush":      {"cloth": 28, "leather": 30, "scale": 32, "chain": 35, "plate": 38},
    "puncture":   {"cloth": 34, "leather": 35, "scale": 31, "chain": 37, "plate": 33},
    "fire":       {"cloth": 25, "leather": 24, "scale": 22, "chain": 20, "plate": 18},
    "cold":       {"cloth": 25, "leather": 24, "scale": 22, "chain": 20, "plate": 18},
    "electrical": {"cloth": 25, "leather": 24, "scale": 22, "chain": 20, "plate": 18},
}

DF_ARMOR_MULT = {
    "slash":      {"cloth": 1.12, "leather": 1.05, "scale": 0.92, "chain": 0.85, "plate": 0.78},
    "crush":      {"cloth": 0.95, "leather": 1.00, "scale": 1.06, "chain": 1.12, "plate": 1.18},
    "puncture":   {"cloth": 1.08, "leather": 1.02, "scale": 0.98, "chain": 1.08, "plate": 0.96},
    "fire":       {"cloth": 1.00, "leather": 1.00, "scale": 1.00, "chain": 1.00, "plate": 1.00},
    "cold":       {"cloth": 1.00, "leather": 1.00, "scale": 1.00, "chain": 1.00, "plate": 1.00},
    "electrical": {"cloth": 1.00, "leather": 1.00, "scale": 1.00, "chain": 1.00, "plate": 1.00},
}

# Critical divisors by Armor Skin Group
CRIT_DIVISORS = {
    1: 5,    # None / robes
    2: 5,    # Robes
    3: 5,    # Soft leather
    4: 6,    # Full leather
    5: 6,    # Light leather
    6: 6,    # Full leather (natural)
    7: 7,    # Scale
    8: 7,    # Chain mail
    9: 9,    # Chain hauberk
    10: 9,   # Augmented chain
    11: 11,  # Half plate
    12: 11,  # Full plate
}

# Stance AS/DS modifiers: (AS_mod, DS_mod)
STANCE_MODS = {
    "offensive": (20, -20),
    "advance": (15, -10),
    "forward": (10, 0),
    "neutral": (0, 0),
    "guarded": (-10, 15),
    "defensive": (-20, 25),
}

# Body locations are now defined in scripts/data/body_types.lua and loaded
# via body_types_loader. The loader is imported above.
# BODY_LOCATIONS is kept as a biped fallback reference for player injury
# tracking (players are always biped).
BODY_LOCATIONS = {
    "head": 5, "neck": 3, "chest": 20, "abdomen": 15, "back": 10,
    "right arm": 10, "left arm": 10, "right hand": 5, "left hand": 5,
    "right leg": 8, "left leg": 8, "right eye": 1, "left eye": 1,
}

# Critical hit flavor text by damage type and severity (1-9)
CRIT_MESSAGES = {
    "slash": {
        1: "Minor cut.",
        2: "Nice slash draws blood.",
        3: "Deep gash opens up!",
        4: "Vicious slash tears flesh!",
        5: "Devastating slash!  Blood sprays everywhere!",
        6: "Horrendous slash rends flesh from bone!",
        7: "Gruesome wound!  Tissue and sinew exposed!",
        8: "Near-severing blow!  Limb barely attached!",
        9: "*** CRITICAL *** Clean dismembering strike!",
    },
    "crush": {
        1: "Glancing blow.",
        2: "Good hit!  Bruising impact.",
        3: "Solid blow cracks bone!",
        4: "Heavy hit shatters bone!",
        5: "Crushing blow!  Bones snap audibly!",
        6: "Devastating impact!  Internal organs damaged!",
        7: "Massive trauma!  Body buckles from the force!",
        8: "Bone-shattering hit!  Structure collapses!",
        9: "*** CRITICAL *** Pulverizing strike!",
    },
    "puncture": {
        1: "Minor prick.",
        2: "Good hit pierces skin.",
        3: "Deep puncture draws blood!",
        4: "Vicious thrust!  Organs may be hit!",
        5: "Devastating thrust!  Clean through-and-through!",
        6: "Impaling strike!  Vital organs pierced!",
        7: "Horrible wound!  Blood pours freely!",
        8: "Near-fatal wound!  Life force fading!",
        9: "*** CRITICAL *** Lethal impalement!",
    },
}

# Lethal critical thresholds by location
LETHAL_THRESHOLDS = {
    "head": 5,
    "neck": 4,
    "chest": 7,
    "abdomen": 8,
    "back": 7,
    "right eye": 3,
    "left eye": 3,
}

LOCATION_DAMAGE_MULT = {
    "head": 1.18, "neck": 1.35, "chest": 1.08, "abdomen": 1.02, "back": 1.00,
    "right eye": 1.45, "left eye": 1.45,
    "right arm": 0.92, "left arm": 0.92,
    "right hand": 0.82, "left hand": 0.82,
    "right leg": 0.95, "left leg": 0.95,
}

LOCATION_CRIT_DIV_MULT = {
    "head": 0.85, "neck": 0.72, "chest": 0.92, "abdomen": 0.96, "back": 1.00,
    "right eye": 0.55, "left eye": 0.55,
    "right arm": 0.88, "left arm": 0.88,
    "right hand": 0.62, "left hand": 0.62,
    "right leg": 0.84, "left leg": 0.84,
}

SEVERABLE_LOCATIONS = {"right arm", "left arm", "right hand", "left hand", "right leg", "left leg"}


def _armor_group_from_asg(armor_asg: int) -> str:
    return ARMOR_GROUP_BY_ASG.get(int(armor_asg or 1), "leather")


def _split_damage_types(raw_damage_type: str | None) -> list[str]:
    raw = str(raw_damage_type or "").strip().lower()
    if not raw:
        return ["crush"]
    types = [part.strip() for part in raw.split(",") if part.strip()]
    return types or ["crush"]


def _resolve_damage_profile(raw_damage_type: str | None, armor_asg: int, base_df: float | None = None) -> dict:
    armor_group = _armor_group_from_asg(armor_asg)
    best = None
    for damage_type in _split_damage_types(raw_damage_type):
        avd = AVD_TABLE.get(damage_type, AVD_TABLE["crush"]).get(armor_group, 30)
        df_base = float(base_df if base_df is not None else DAMAGE_FACTORS.get(damage_type, 0.25))
        df = df_base * DF_ARMOR_MULT.get(damage_type, DF_ARMOR_MULT["crush"]).get(armor_group, 1.0)
        score = avd + (df * 100.0)
        candidate = {
            "damage_type": damage_type,
            "armor_group": armor_group,
            "avd": avd,
            "df": df,
            "score": score,
        }
        if best is None or candidate["score"] > best["score"]:
            best = candidate
    return best or {"damage_type": "crush", "armor_group": armor_group, "avd": 30, "df": 0.25, "score": 55.0}


def _get_player_weapon(session):
    """Get the PRIMARY (right hand) weapon. Returns (item_dict, hand_name) or (None, None)."""
    if session.right_hand and session.right_hand.get('item_type') == 'weapon':
        return session.right_hand, 'right'
    if session.left_hand and session.left_hand.get('item_type') == 'weapon':
        return session.left_hand, 'left'
    return None, None


def _get_offhand_weapon(session):
    """Get the off-hand (left) weapon if TWC is in effect. Returns item_dict or None."""
    rh = session.right_hand
    lh = session.left_hand
    # Both hands must have weapons for TWC
    if (rh and rh.get('item_type') == 'weapon' and
            lh and lh.get('item_type') == 'weapon'):
        return lh
    return None


def _calc_twc_rt(session, main_weapon, off_weapon):
    """
    Calculate TWC roundtime.
    TWCBaseSpeed = RightBaseSpeed + max(LeftBaseSpeed - 2, 0) + max(WeightPenalty, 0)
    STROffset = (STRBonus + 10) // 15
    WeightPenalty = min(LeftWeight - 2 - STROffset, 3)
    """
    right_speed = float(main_weapon.get('weapon_speed', 5)) if main_weapon else 5.0
    left_speed  = float(off_weapon.get('weapon_speed', 3))  if off_weapon else 3.0
    left_weight = float(off_weapon.get('weight', 2))        if off_weapon else 2.0

    str_bonus   = (getattr(session, 'stat_strength', 50) - 50) // 2
    str_offset  = (str_bonus + 10) // 15
    weight_pen  = min(max(left_weight - 2 - str_offset, 0), 3)

    base_rt = right_speed + max(left_speed - 2, 0) + weight_pen
    return max(3, min(base_rt, 9))


def _calc_twc_offhand_as(session, off_weapon):
    """
    GS4 wiki: off-hand AS uses the SAME formula as main hand AS.
    Melee AS = STR Bonus + Weapon Skill Bonus + [CM Ranks / 2]
             + Weapon Enchantment + Modifiers
    Stance multiplies the entire total (100% OFF -> 50% DEF).
    TWC training reduces the off-hand penalty; without it the off-hand
    takes a flat -25 to raw AS before stance is applied.
    No level base — that does not exist in the GS4 formula.
    """
    # Wiki formula components — mirrors _calc_player_as exactly
    str_bonus = (getattr(session, 'stat_strength', 50) - 50) // 2
    cm_bonus  = _sr(session, SKILL_COMBAT_MANEUVERS) // 2

    # Off-hand weapon skill
    off_cat = off_weapon.get('weapon_category', 'edged') if off_weapon else 'edged'
    off_skill_id = {
        'edged':     SKILL_EDGED_WEAPONS,
        'blunt':     SKILL_BLUNT_WEAPONS,
        'twohanded': SKILL_TWO_HANDED,
        'polearm':   SKILL_POLEARM,
        'ranged':    SKILL_RANGED,
        'thrown':    SKILL_THROWN,
        'brawling':  SKILL_BRAWLING,
    }.get(off_cat, SKILL_EDGED_WEAPONS)
    off_skill_bonus = _sb(session, off_skill_id)

    # Enchant — same overage penalty as main hand
    raw_enc = off_weapon.get('enchant_bonus', 0) or 0 if off_weapon else 0
    enchant = _calc_effective_enchant(session.level, raw_enc)

    attack_bonus = off_weapon.get('attack_bonus', 0) if off_weapon else 0

    # TWC training — reduces the off-hand penalty
    # Without any TWC ranks: -25 to raw AS (GS4 wiki: significant penalty untrained)
    # Each TWC rank contributes its bonus/3 and reduces the penalty
    twc_bonus  = _sb(session, SKILL_TWC)
    twc_penalty = max(0, 25 - twc_bonus // 2)

    raw_as = str_bonus + off_skill_bonus + cm_bonus + enchant + attack_bonus + (twc_bonus // 3) - twc_penalty

    # Stance multiplies the entire AS value — same as main hand
    stance_mult = {
        "offensive": 1.00,
        "advance":   0.90,
        "forward":   0.80,
        "neutral":   0.70,
        "guarded":   0.60,
        "defensive": 0.50,
    }.get(session.stance, 0.70)
    as_val = int(raw_as * stance_mult)

    # Injury penalty (post-stance, same as main hand)
    injuries = getattr(session, 'injuries', {})
    for loc, sev in injuries.items():
        if loc in ('left_arm', 'left_hand') and sev >= 3:
            as_val -= sev * 3

    as_val = int(as_val * getattr(session, 'death_stat_mult', 1.0))

    # Encumbrance penalty applies to off-hand AS same as main hand
    as_val += encumbrance_as_ds_penalty(session)

    return as_val





    # ================================================================
    # Player attacks creature
    # ================================================================


def _get_weapon_name(weapon):
    """Get display name for a weapon item."""
    if weapon:
        article = weapon.get('article', 'a')
        name = weapon.get('short_name') or weapon.get('name') or 'something'
        return f"{article} {name}" if article else name
    return None


def _get_player_shield(session):
    """Get the player's actively worn shield.
    Must be in an arm/active slot — shoulder_slung means it's on their back,
    not being used, and provides no DS or block."""
    for item in getattr(session, 'inventory', []):
        if item.get('item_type') == 'shield' and item.get('slot') in ('worn_shield', 'left_arm', 'arm'):
            return item
    return None


def _get_player_armor(session):
    """Get the player's worn armor from inventory."""
    for item in getattr(session, 'inventory', []):
        if item.get('slot') == 'torso' and item.get('item_type') == 'armor':
            return item
    return None


def _calc_effective_enchant(player_level: int, enchant_bonus: int) -> int:
    """
    GS4 enchant overage mechanic.
    Max usable enchant = player_level * 2.
    Any enchant above that threshold penalizes AS/DS harder than it helps.
    Overage penalty = overage * 2, so net effect = enchant - overage * 2
    which means above the threshold you're actively worse than a plain weapon.

    Examples:
      Level 5, +10 weapon  -> max=10, overage=0,  effective=+10  (full benefit)
      Level 5, +15 weapon  -> max=10, overage=5,  effective=+5   (partial)
      Level 5, +20 weapon  -> max=10, overage=10, effective=-10  (worse than steel!)
      Level 5, +25 weapon  -> max=10, overage=15, effective=-20
    """
    if enchant_bonus <= 0:
        return enchant_bonus
    max_usable = player_level * 2
    overage = max(0, enchant_bonus - max_usable)
    return enchant_bonus - (overage * 2)



def _enter_combat(server, session, creature):
    sm = getattr(server, 'status', None)
    if sm:
        sm.enter_combat(session, creature)
        sm.refresh_combat(creature)
    else:
        session.in_combat  = True
        session.target     = creature
        creature.in_combat = True
        creature.target    = session


def _exit_combat(server, session):
    sm = getattr(server, 'status', None)
    if sm:
        sm.exit_combat(session)
    else:
        session.in_combat = False
        session.target    = None


def _refresh_combat(server, session, creature):
    sm = getattr(server, 'status', None)
    if sm:
        sm.refresh_combat(session, creature)
        sm.refresh_combat(creature)
    else:
        session.in_combat  = True
        creature.in_combat = True


class CombatEngine:
    """Handles all combat resolution with GS4-authentic messaging."""

    _STANCE_ORDER = ["offensive", "advance", "forward", "neutral", "guarded", "defensive"]
    _STANCE_DS_BONUS = {
        "offensive": -20,
        "advance": -10,
        "forward": 0,
        "neutral": 0,
        "guarded": 15,
        "defensive": 25,
    }

    def __init__(self, server):
        self.server = server

    def _get_ambush_cfg(self) -> dict:
        return getattr(self.server, "ambush_cfg", {}) or {}

    def _get_weapon_category(self, weapon) -> str:
        if not weapon:
            return "unarmed"
        return (weapon.get("weapon_category", "edged") or "edged").lower()

    def _get_weapon_base_name(self, weapon) -> str:
        if not weapon:
            return ""
        return str(weapon.get("base_name", "") or "").lower()

    def _get_ambush_skill_bonus(self, session) -> int:
        cfg = self._get_ambush_cfg()
        ambush_skill_id = int(cfg.get("skill_id", 43))
        bonus = _sb(session, ambush_skill_id)
        if ambush_skill_id != 26 and bonus <= 0:
            return _sb(session, 26)
        return bonus

    def _get_ambush_skill_ranks(self, session) -> int:
        cfg = self._get_ambush_cfg()
        ambush_skill_id = int(cfg.get("skill_id", 43))
        ranks = _sr(session, ambush_skill_id)
        if ambush_skill_id != 26 and ranks <= 0:
            return _sr(session, 26)
        return ranks

    def _get_ambush_cm_bonus(self, session) -> int:
        cfg = self._get_ambush_cfg()
        return _sb(session, int(cfg.get("cm_skill_id", SKILL_COMBAT_MANEUVERS)))

    def _calc_hidden_ambush_steps(self, ambush_bonus: int, creature_level: int) -> int:
        hidden_cfg = self._get_ambush_cfg().get("hidden", {}) or {}
        push_cfg = hidden_cfg.get("stance_pushdown", {}) or {}
        min_steps = max(0, int(push_cfg.get("minimum_steps", 1) or 0))
        max_steps = max(min_steps, int(push_cfg.get("max_steps", 4) or 4))
        level_scale = float(push_cfg.get("level_scale", 3) or 3)
        bonus_step_every = max(1, int(push_cfg.get("bonus_step_every", 60) or 60))
        diff = int(ambush_bonus - (creature_level * level_scale))
        extra_steps = max(0, diff) // bonus_step_every
        return min(max_steps, min_steps + extra_steps)

    def _calc_hidden_ambush_profile(self, session, creature, weapon, creature_ds: int) -> dict:
        cfg = self._get_ambush_cfg()
        hidden_cfg = cfg.get("hidden", {}) or {}
        ambush_bonus = self._get_ambush_skill_bonus(session)
        ambush_ranks = self._get_ambush_skill_ranks(session)
        weapon_cat = self._get_weapon_category(weapon)
        weapon_base = self._get_weapon_base_name(weapon)

        current_stance = (getattr(creature, "stance", "neutral") or "neutral").lower()
        if current_stance not in self._STANCE_ORDER:
            current_stance = "neutral"
        current_idx = self._STANCE_ORDER.index(current_stance)
        push_steps = self._calc_hidden_ambush_steps(ambush_bonus, getattr(creature, "level", 1))
        pushed_idx = max(0, current_idx - push_steps)
        pushed_stance = self._STANCE_ORDER[pushed_idx]

        current_stance_bonus = self._STANCE_DS_BONUS.get(current_stance, 0)
        pushed_stance_bonus = self._STANCE_DS_BONUS.get(pushed_stance, 0)
        stance_reduction = max(0, current_stance_bonus - pushed_stance_bonus)

        ebp_share = max(0.0, float(hidden_cfg.get("ebp_ds_share", 0.30) or 0.30))
        ebp_reduction_pct = max(0.0, float(hidden_cfg.get("ebp_reduction_pct", 0.50) or 0.50))
        ebp_reduction = int(max(0, creature_ds) * ebp_share * ebp_reduction_pct)

        weapon_as_bonus = hidden_cfg.get("weapon_as_bonus", {}) or {}
        favored_weapons = hidden_cfg.get("favored_weapons", {}) or {}
        favored_weapon_cfg = favored_weapons.get(weapon_base, {}) if weapon_base else {}
        as_bonus = 0
        if weapon:
            as_bonus += int(hidden_cfg.get("any_weapon_as_bonus", 0) or 0)
            as_bonus += int(weapon_as_bonus.get(weapon_cat, weapon_as_bonus.get("default", 0)) or 0)
            as_bonus += int(favored_weapon_cfg.get("as_bonus", 0) or 0)

        crit_cfg = hidden_cfg.get("crit_weighting", {}) or {}
        bonus_divisor = max(1, int(crit_cfg.get("bonus_divisor", 30) or 30))
        rank_divisor = max(1, int(crit_cfg.get("rank_divisor", 12) or 12))
        weapon_crit_bonus = crit_cfg.get("weapon_bonus", {}) or {}
        crit_phantom = 0
        if weapon:
            crit_phantom += ambush_bonus // bonus_divisor
            crit_phantom += ambush_ranks // rank_divisor
            crit_phantom += int(crit_cfg.get("any_weapon_flat", 0) or 0)
            crit_phantom += int(weapon_crit_bonus.get(weapon_cat, weapon_crit_bonus.get("default", 0)) or 0)
            crit_phantom += int(favored_weapon_cfg.get("crit_flat", 0) or 0)

        return {
            "as_bonus": as_bonus,
            "crit_phantom": max(0, crit_phantom),
            "creature_ds": max(0, creature_ds - stance_reduction - ebp_reduction),
            "rt_reduction": max(0, int(hidden_cfg.get("rt_reduction", 1) or 0)),
        }

    # ================================================================
    # Player attacks creature
    # ================================================================
    async def player_attacks_creature(self, session, creature, aimed_location=None,
                                       is_ambush=False):
        """
        Resolve a player melee attack against a creature.
        Returns True if creature dies.
        """
        # No weapon — route to UCS (Unarmed Combat System)
        weapon, weapon_hand = _get_player_weapon(session)
        if not weapon:
            return await self._ucs_punch_attack(session, creature)

        weapon_name = _get_weapon_name(weapon)
        cman_ctx = dict(getattr(session, "combat_maneuver_attack_context", None) or {})
        session.combat_maneuver_attack_context = None
        session.combat_maneuver_last_attack = None

        # Calculate player AS
        player_as = self._calc_player_as(session)
        player_as += int(cman_ctx.get("as_bonus", 0) or 0)

        # Calculate creature DS (feint debuff lowers it temporarily)
        creature_ds = creature.get_melee_ds()
        import time as _ft
        feint_until = getattr(creature, "_feint_until", 0)
        if feint_until > _ft.time():
            creature_ds = creature_ds // 2  # feint halves creature DS for one attack
        ebp_reduce_pct = int(cman_ctx.get("ebp_reduce_pct", 0) or 0)
        if ebp_reduce_pct > 0:
            creature_ds = max(0, int(creature_ds * (1.0 - (ebp_reduce_pct / 100.0))))

        ambush_profile = None
        if is_ambush:
            ambush_profile = self._calc_hidden_ambush_profile(session, creature, weapon, creature_ds)
            creature_ds = ambush_profile["creature_ds"]
            player_as += ambush_profile["as_bonus"]

        # Roll
        roll_floor = int(cman_ctx.get("roll_floor", 0) or 0)
        roll_sides = int(cman_ctx.get("roll_sides", 0) or 0)
        if roll_floor > 0 and roll_sides > 0:
            d100 = roll_floor + random.randint(1, max(1, roll_sides))
        else:
            d100 = random.randint(1, 100)
        endroll = None

        # Determine hit location — respects session.aimed_location and does aim roll
        location, aim_succeeded = self._resolve_hit_location(
            session, creature, aimed_location_override=aimed_location, hidden_ambush=is_ambush
        )

        profile = _resolve_damage_profile(
            weapon.get('damage_type', 'slash') if weapon else "crush",
            getattr(creature, "armor_asg", 5),
            weapon.get('damage_factor', 0) or None if weapon else None,
        )
        damage_type = profile["damage_type"]
        weapon_df = profile["df"]
        weapon_df *= float(cman_ctx.get("df_mult", 1.0) or 1.0)
        avd = profile["avd"]
        endroll = d100 + player_as - creature_ds + avd

        # Build the attack line (GS4 format)
        creature_display = fmt_creature_name(creature.full_name_with_level)

        if weapon_name:
            swing_line = f"You swing {weapon_name} at {creature_display}!"
        else:
            swing_line = f"You punch at {creature_display}!"

        # Roll line (GS4 format: "AS: +82 vs DS: +30 with AvD: +35 + d100 roll: +74 = +161")
        roll_line = (
            f"  AS: {'+' if player_as >= 0 else ''}{player_as} vs "
            f"DS: {'+' if creature_ds >= 0 else ''}{creature_ds} with "
            f"AvD: {'+' if avd >= 0 else ''}{avd} + "
            f"d100 roll: +{d100} = {'+' if endroll >= 0 else ''}{endroll}"
        )

        # Miss
        if endroll <= 100:
            await session.send_line(swing_line)
            await session.send_line(colorize(roll_line, TextPresets.COMBAT_MISS))
            await session.send_line("  A clean miss.")

            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"{session.character_name} swings at {creature.full_name} but misses!\n"
                f"  {roll_line}",
                exclude=session
            )

            # TWC: off-hand always swings regardless of main-hand result
            off_weapon = _get_offhand_weapon(session)
            if off_weapon:
                rt = _calc_twc_rt(session, weapon, off_weapon)
            else:
                rt = 5
            if is_ambush:
                rt = max(3, rt - (ambush_profile["rt_reduction"] if ambush_profile else 1))
            rt += int(cman_ctx.get("roundtime_modifier", 0) or 0)
            rt += encumbrance_rt_penalty(session)
            rt = apply_roundtime_effects(rt, self.server, session)
            rt = max(3, min(rt, 12))
            session.set_roundtime(rt)
            await session.send_line(roundtime_msg(rt))
            session.combat_maneuver_last_attack = {
                "hit": False,
                "damage": 0,
                "endroll": endroll,
                "killed": False,
            }
            consume_on_attack_bonuses(session)

            _enter_combat(self.server, session, creature)
            if off_weapon:
                offhand_killed = await self._twc_offhand_swing(
                    session,
                    creature,
                    off_weapon,
                    is_ambush,
                    aimed_location=aimed_location,
                )
                if offhand_killed:
                    return True
            _refresh_combat(self.server, session, creature)
            return False

        # Hit! Calculate damage
        loc_df_mult = LOCATION_DAMAGE_MULT.get(location, 1.0)
        raw_damage = max(1, int((endroll - 100) * weapon_df * loc_df_mult))

        # Critical calculation — material crit_weight adds CEP phantom points to
        # raw_damage before the divisor (razern = +2).  HP damage uses original
        # raw_damage only; phantom points raise the crit rank floor exclusively.
        crit_phantom  = get_crit_phantom(weapon, self.server.lua)
        if ambush_profile:
            crit_phantom += ambush_profile["crit_phantom"]
        crit_phantom += int(cman_ctx.get("crit_phantom", 0) or 0)
        adj_raw       = raw_damage + crit_phantom
        crit_divisor  = max(1, int(CRIT_DIVISORS.get(creature.armor_asg, 5) * LOCATION_CRIT_DIV_MULT.get(location, 1.0)))
        crit_rank_max = min(9, adj_raw // crit_divisor)

        if crit_rank_max > 0:
            crit_rank_min = max(1, (crit_rank_max + 1) // 2)
            crit_rank = random.randint(crit_rank_min, crit_rank_max)
        else:
            crit_rank = 0

        # Scale HP damage (original raw_damage — phantom does not inflate HP)
        hp_damage = max(1, int((endroll - 100) * (0.42 + (weapon_df * 0.25)) * loc_df_mult) + crit_rank * 3)
        actual_damage = creature.take_damage(hp_damage)

        # ── Weapon elemental flare proc ────────────────────────────────────────
        # Counter-based: fires every 5th successful hit per weapon slot.
        # Flare damage stacks on top of normal hit damage.
        flare_result = await resolve_flare(session, creature, weapon, weapon_hand)
        if flare_result:
            flare_dmg = flare_result.get("damage", 0)
            if flare_dmg > 0:
                creature.take_damage(flare_dmg)
        holy_flare_dmg = _holy_flare_damage(session, self.server)
        if holy_flare_dmg > 0:
            creature.take_damage(holy_flare_dmg)

        # Build output lines
        await session.send_line(swing_line)
        await session.send_line(colorize(roll_line, TextPresets.COMBAT_HIT))
        await session.send_line(colorize(
            f"  ... and hit for {actual_damage} points of damage!",
            TextPresets.COMBAT_HIT
        ))
        if flare_result:
            await session.send_line(colorize(
                f"  {flare_result.get('attacker_msg', '')}",
                TextPresets.COMBAT_HIT
            ))
            if flare_result.get("damage", 0) > 0:
                await session.send_line(colorize(
                    f"  The flare deals {flare_result['damage']} additional points of damage!",
                    TextPresets.COMBAT_HIT
                ))
            room_msg = flare_result.get("room_msg", "")
            if room_msg:
                await self.server.world.broadcast_to_room(
                    session.current_room.id,
                    colorize(f"  {room_msg}", TextPresets.COMBAT_HIT),
                    exclude=[session],
                )
        if holy_flare_dmg > 0:
            await session.send_line(colorize(
                f"  Holy fire lashes out for {holy_flare_dmg} additional points of damage!",
                TextPresets.COMBAT_HIT
            ))
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                colorize(f"  A burst of holy fire erupts from {session.character_name}'s strike!", TextPresets.COMBAT_HIT),
                exclude=[session],
            )

        # Aim drift notification — show only if player was aiming somewhere specific
        _requested_aim = aimed_location or getattr(session, "aimed_location", None)
        if _requested_aim:
            _body_type = getattr(creature, "body_type", "biped") or "biped"
            _valid_aim = resolve_aim(_body_type, _requested_aim)
            if not _valid_aim:
                # Creature doesn't have this location (e.g. aiming at "right hand" vs a snake)
                await session.send_line(colorize(
                    f"  The {creature.name} has no {_requested_aim} to target — striking at random!",
                    TextPresets.SYSTEM
                ))
            elif not aim_succeeded:
                # Had a valid location but the aim roll failed — drifted
                await session.send_line(colorize(
                    f"  Your aim drifts — striking the {location} instead!",
                    TextPresets.SYSTEM
                ))

        await session.send_line(combat_damage(actual_damage, location))

        if crit_rank > 0:
            crit_msgs = CRIT_MESSAGES.get(damage_type, CRIT_MESSAGES["slash"])
            crit_msg = crit_msgs.get(crit_rank, "Critical hit!")
            await session.send_line(combat_crit(crit_rank, crit_msg))

        # ── Apply wound to creature at hit location ───────────────────────────
        # All crit rank 1+ cause wounds; severity scales with rank
        if crit_rank >= 1:
            old_sev = creature.wounds.get(location, 0)
            new_sev = creature.apply_wound(location, crit_rank)

            SEV_NAMES = {1: "minor", 2: "moderate", 3: "major", 4: "severe", 5: "crippling"}
            DEGRADE_MSGS = {
                2: f"  {creature.full_name.capitalize()} winces, its movements becoming less precise!",
                3: f"  {creature.full_name.capitalize()} staggers, noticeably hampered by its wounds!",
                4: f"  {creature.full_name.capitalize()} struggles to fight effectively — its wounds are severe!",
                5: f"  {creature.full_name.capitalize()} can barely stand!  It fights desperately!",
            }

            # Announce wound if it worsened
            if new_sev > old_sev:
                sev_name = SEV_NAMES.get(new_sev, "wounded")
                await session.send_line(colorize(
                    f"  {creature.full_name.capitalize()} suffers a {sev_name} wound to its {location}!",
                    TextPresets.COMBAT_HIT
                ))
                impairment = creature.evaluate_combat_impairment(location, old_sev, new_sev)
                if impairment.get("dropped_weapon"):
                    await session.send_line(colorize(
                        f"  {creature.full_name.capitalize()} drops its weapon as the limb goes slack!",
                        TextPresets.COMBAT_HIT
                    ))
                if impairment.get("severed") and location in SEVERABLE_LOCATIONS:
                    await session.send_line(colorize(
                        f"  The strike severs {creature.full_name}'s {location}!",
                        TextPresets.COMBAT_HIT
                    ))
                if impairment.get("stance_shift"):
                    creature.stance = impairment["stance_shift"]

                # Show a combat-stat-degradation message at key severity thresholds
                if new_sev in DEGRADE_MSGS and old_sev < new_sev:
                    await session.send_line(colorize(
                        DEGRADE_MSGS[new_sev], TextPresets.COMBAT_HIT
                    ))

        # Stun on crit rank 3+
        if crit_rank >= 3:
            stun_dur = crit_rank * 2
            creature.stun(stun_dur)
            await session.send_line(colorize(
                f"  The {creature.name} is stunned!",
                TextPresets.COMBAT_HIT
            ))

        # Bleed on crit rank 3+, fear on rank 6+
        if crit_rank >= 3:
            try:
                from server.core.engine.combat.status_effects import apply_bleed, apply_fear
                apply_bleed(creature, crit_rank, attacker=session)
                await session.send_line(colorize(
                    f"  {creature.full_name.capitalize()} is bleeding!",
                    TextPresets.COMBAT_HIT
                ))
                if crit_rank >= 6:
                    apply_fear(creature, duration=30)
                    await session.send_line(colorize(
                        f"  {creature.full_name.capitalize()} looks terrified!",
                        TextPresets.COMBAT_HIT
                    ))
            except ImportError:
                pass

        # HP-milestone degradation messages (show once per threshold crossed)
        hp_pct = creature.health_current / creature.health_max if creature.health_max > 0 else 0
        prev_hp_pct = (creature.health_current + actual_damage) / creature.health_max if creature.health_max > 0 else 1
        HP_THRESHOLDS = {
            0.50: f"  {creature.full_name.capitalize()} is badly wounded!",
            0.25: f"  {creature.full_name.capitalize()} looks nearly defeated!",
            0.10: f"  {creature.full_name.capitalize()} is on the verge of collapse!",
        }
        for threshold, msg in HP_THRESHOLDS.items():
            if prev_hp_pct > threshold >= hp_pct:
                await session.send_line(colorize(msg, TextPresets.COMBAT_HIT))
                break

        # Broadcast full roll info to observers
        crit_obs = f"  Crit rank {crit_rank}!" if crit_rank > 0 else ""
        await self.server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} swings at {creature.full_name} and connects!\n"
            f"  {roll_line}\n"
            f"  Hit for {actual_damage} points of damage to the {location}.{chr(10) + crit_obs if crit_obs else ''}",
            exclude=session
        )
        if cman_ctx.get("force_target_stance"):
            order = ["defensive", "guarded", "neutral", "forward", "advance", "offensive"]
            current = str(getattr(creature, "stance", "neutral") or "neutral").lower()
            if current not in order:
                current = "neutral"
            creature.stance = order[min(len(order) - 1, order.index(current) + 1)]

        # Check death
        killed = False
        if creature.is_dead or (crit_rank >= LETHAL_THRESHOLDS.get(location, 99)):
            if not creature.is_dead:
                creature.take_damage(creature.health_current)
            killed = True
            await session.send_line(combat_death(creature.full_name.capitalize()))
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"  {creature.full_name.capitalize()} falls to the ground dead!",
                exclude=session
            )
            self.server.creatures.mark_dead(creature)
            session.target = None
            remaining = [
                c for c in self.server.creatures.get_creatures_in_room(session.current_room.id)
                if c.alive and c.aggressive and c is not creature
            ]
            if not remaining:
                _exit_combat(self.server, session)

            if not session.tutorial_complete and hasattr(self.server, 'tutorial'):
                await self.server.tutorial.on_creature_death(session, creature)

            if hasattr(self.server, 'experience'):
                from server.core.commands.player.party import award_party_kill_xp; await award_party_kill_xp(session, creature, self.server)

            if self.server.db and session.character_id:
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current, session.mana_current,
                    session.spirit_current, session.stamina_current,
                    session.silver
                )
        else:
            if self.server.db and session.character_id:
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current, session.mana_current,
                    session.spirit_current, session.stamina_current,
                    session.silver
                )

        # Roundtime - TWC uses combined weapon speed formula
        off_weapon = _get_offhand_weapon(session)
        if off_weapon:
            rt = _calc_twc_rt(session, weapon, off_weapon)
        else:
            rt = weapon.get('weapon_speed', 5) if weapon else 5
        if is_ambush:
            rt = max(3, rt - (ambush_profile["rt_reduction"] if ambush_profile else 1))
        rt += int(cman_ctx.get("roundtime_modifier", 0) or 0)
        # Encumbrance adds to RT (stacks on top of weapon speed)
        rt += encumbrance_rt_penalty(session)
        rt = apply_roundtime_effects(rt, self.server, session)
        rt = max(3, min(rt, 12))   # floor 3, cap 12
        session.set_roundtime(rt)
        await session.send_line(roundtime_msg(rt))
        session.combat_maneuver_last_attack = {
            "hit": True,
            "damage": actual_damage,
            "endroll": endroll,
            "killed": killed,
            "location": location,
        }
        consume_on_attack_bonuses(session)

        # Enter / refresh combat state
        if not killed:
            _enter_combat(self.server, session, creature)

        # ── TWC off-hand swing — always fires, no strike chance check ─────────
        if not killed and off_weapon:
            offhand_killed = await self._twc_offhand_swing(
                session,
                creature,
                off_weapon,
                is_ambush,
                aimed_location=aimed_location,
            )
            if offhand_killed:
                killed = True   # offhand finished the kill — don't re-enter combat
        if not killed:
            _refresh_combat(self.server, session, creature)

        return killed

    # ================================================================
    # UCS (Unarmed Combat System) — punch/kick/jab when no weapon held
    # ================================================================
    async def _ucs_punch_attack(self, session, creature):
        """Resolve an unarmed punch using the GS4 UCS system.

        Wiki formula:
          endroll = trunc(UAF / UDF × MM) + d100
          hit if endroll > 100

        MM starts at 100 (Tier 1 / decent positioning).
        Stance penalizes MM: offensive=+20, forward=+10, neutral=0,
          guarded=-15, defensive=-25  (mirrors AS stance deltas applied to MM).
        UAF is NOT affected by stance.
        """
        if creature.is_dead:
            return False

        uaf = self._calc_player_uaf(session)
        # udf=0 in mob lua means "not explicitly set" — fall back to ds_melee,
        # which is the creature's actual melee defense stat for UCS combat.
        if hasattr(creature, "get_udf"):
            udf = max(1, int(creature.get_udf() or 1))
        else:
            _raw_udf = getattr(creature, 'udf', 0)
            udf = max(1, _raw_udf if _raw_udf > 0 else getattr(creature, 'ds_melee', creature.level * 3))

        # Tier 1 (decent) base MM — stance penalizes MM per wiki note
        mm_stance = {
            "offensive": 20, "advance": 10, "forward": 5,
            "neutral": 0, "guarded": -15, "defensive": -25,
        }
        mm = 100 + mm_stance.get(session.stance, 0)

        d100    = random.randint(1, 100)
        ratio   = uaf / udf
        endroll = int(ratio * mm) + d100

        creature_display = fmt_creature_name(creature.full_name_with_level)
        swing_line = f"You punch at {creature_display}!"
        roll_line  = (
            f"  You have decent positioning against {creature.full_name}.\n"
            f"  UAF: {uaf} vs UDF: {udf} = {ratio:.3f} * MM: {mm} + d100: {d100} = {endroll}"
        )

        # Miss
        if endroll <= 100:
            await session.send_line(swing_line)
            await session.send_line(colorize(roll_line, TextPresets.COMBAT_MISS))
            await session.send_line("  A clean miss.")
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"{session.character_name} swings a fist at {creature.full_name} but misses!",
                exclude=session
            )
            session.set_roundtime(3)
            await session.send_line(roundtime_msg(3))
            session.in_combat = True
            session.target    = creature
            creature.in_combat = True
            creature.target   = session
            session.combat_maneuver_last_attack = {
                "hit": False,
                "damage": 0,
                "endroll": endroll,
                "killed": False,
            }
            consume_on_attack_bonuses(session)
            return False

        # Hit — UCS damage uses punch DF by armor group (wiki table)
        # ASG → armor group: 1=cloth, 2-9=leather, 10-13=scale, 14-17=chain, 18-20=plate
        asg = getattr(creature, 'armor_asg', 1)
        if asg <= 1:
            punch_df = 0.275   # cloth
        elif asg <= 9:
            punch_df = 0.250   # leather
        elif asg <= 13:
            punch_df = 0.200   # scale
        elif asg <= 17:
            punch_df = 0.170   # chain
        else:
            punch_df = 0.140   # plate

        raw_damage  = max(1, int((endroll - 100) * punch_df))
        crit_divisor  = CRIT_DIVISORS.get(asg, 5)
        crit_rank_max = min(5, raw_damage // crit_divisor)   # Tier 1 cap rank 5
        crit_rank     = (random.randint(max(1, (crit_rank_max + 1) // 2), crit_rank_max)
                         if crit_rank_max > 0 else 0)
        hp_damage     = max(1, int((endroll - 100) * 0.4) + crit_rank * 2)
        actual_damage = creature.take_damage(hp_damage)
        _bt           = getattr(creature, 'body_type', 'biped') or 'biped'
        location, _   = self._resolve_hit_location(session, creature)

        await session.send_line(swing_line)
        await session.send_line(colorize(roll_line, TextPresets.COMBAT_HIT))
        await session.send_line(colorize(
            f"  ... and hit for {actual_damage} points of damage!",
            TextPresets.COMBAT_HIT
        ))
        await session.send_line(combat_damage(actual_damage, location))

        if crit_rank > 0:
            crit_msg = CRIT_MESSAGES["crush"].get(crit_rank, "Solid hit!")
            await session.send_line(combat_crit(crit_rank, crit_msg))

        if crit_rank >= 3:
            creature.stun(crit_rank * 2)
            await session.send_line(colorize(
                f"  The {creature.name} is stunned!", TextPresets.COMBAT_HIT
            ))
            try:
                from server.core.engine.combat.status_effects import apply_bleed
                apply_bleed(creature, crit_rank, attacker=session)
                await session.send_line(colorize(
                    f"  {creature.full_name.capitalize()} is bleeding!", TextPresets.COMBAT_HIT
                ))
            except ImportError:
                pass

        await self.server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} strikes {creature.full_name} with a bare fist!",
            exclude=session
        )

        killed = False
        if creature.is_dead or crit_rank >= LETHAL_THRESHOLDS.get(location, 99):
            if not creature.is_dead:
                creature.take_damage(creature.health_current)
            killed = True
            await session.send_line(combat_death(creature.full_name.capitalize()))
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"  {creature.full_name.capitalize()} falls to the ground dead!",
                exclude=session
            )
            self.server.creatures.mark_dead(creature)
            session.target = None
            remaining = [
                c for c in self.server.creatures.get_creatures_in_room(session.current_room.id)
                if c.alive and c.aggressive and c is not creature
            ]
            if not remaining:
                _exit_combat(self.server, session)
            if not session.tutorial_complete and hasattr(self.server, 'tutorial'):
                await self.server.tutorial.on_creature_death(session, creature)
            if hasattr(self.server, 'experience'):
                from server.core.commands.player.party import award_party_kill_xp; await award_party_kill_xp(session, creature, self.server)
            if self.server.db and session.character_id:
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current, session.mana_current,
                    session.spirit_current, session.stamina_current, session.silver
                )
        else:
            _enter_combat(self.server, session, creature)
            if self.server.db and session.character_id:
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current, session.mana_current,
                    session.spirit_current, session.stamina_current, session.silver
                )

        session.set_roundtime(3)   # punch base RT per wiki
        await session.send_line(roundtime_msg(3))
        session.combat_maneuver_last_attack = {
            "hit": True,
            "damage": actual_damage,
            "endroll": endroll,
            "killed": killed,
            "location": location,
        }
        consume_on_attack_bonuses(session)
        return killed

    # ================================================================
    # Creature attacks player
    # ================================================================
    async def _twc_offhand_swing(self, session, creature, off_weapon, is_ambush, aimed_location=None):
        """
        Resolve the TWC off-hand swing. Separate roll with its own AS,
        reduced by TWC training level. No roundtime added (already accounted for).
        """
        if creature.is_dead:
            return

        # Off-hand always swings — training only affects AS, not whether swing fires
        off_as = _calc_twc_offhand_as(session, off_weapon)
        creature_ds = creature.get_melee_ds()
        if is_ambush:
            ambush_profile = self._calc_hidden_ambush_profile(session, creature, off_weapon, creature_ds)
            creature_ds = ambush_profile["creature_ds"]
            off_as += ambush_profile["as_bonus"]
        else:
            ambush_profile = None

        d100     = random.randint(1, 100)
        location, aim_succeeded = self._resolve_hit_location(
            session,
            creature,
            aimed_location_override=aimed_location,
            hidden_ambush=is_ambush,
        )
        profile = _resolve_damage_profile(
            off_weapon.get('damage_type', 'slash'),
            getattr(creature, "armor_asg", 5),
            off_weapon.get('damage_factor', 0) or None,
        )
        damage_type = profile["damage_type"]
        weapon_df   = profile["df"]
        avd         = profile["avd"]
        endroll  = d100 + off_as - creature_ds + avd

        off_name = _get_weapon_name(off_weapon)
        swing_line = f"  You also swing {off_name} at {fmt_creature_name(creature.full_name_with_level)}!"
        roll_line  = (
            f"    AS: {'+' if off_as >= 0 else ''}{off_as} vs "
            f"DS: {'+' if creature_ds >= 0 else ''}{creature_ds} with "
            f"AvD: {'+' if avd >= 0 else ''}{avd} + "
            f"d100 roll: +{d100} = {'+' if endroll >= 0 else ''}{endroll}"
        )

        await session.send_line(swing_line)

        if endroll <= 100:
            await session.send_line(colorize(roll_line, TextPresets.COMBAT_MISS))
            await session.send_line("    Off-hand misses.")
            return

        # Hit — off-hand also gets material crit_weight and flare proc
        loc_df_mult   = LOCATION_DAMAGE_MULT.get(location, 1.0)
        raw_damage    = max(1, int((endroll - 100) * weapon_df * loc_df_mult))
        crit_phantom  = get_crit_phantom(off_weapon, self.server.lua)
        if ambush_profile:
            crit_phantom += ambush_profile["crit_phantom"]
        adj_raw       = raw_damage + crit_phantom
        crit_divisor  = max(1, int(CRIT_DIVISORS.get(creature.armor_asg, 5) * LOCATION_CRIT_DIV_MULT.get(location, 1.0)))
        crit_rank_max = min(9, adj_raw // crit_divisor)
        crit_rank     = random.randint(max(1, (crit_rank_max + 1) // 2), crit_rank_max) if crit_rank_max > 0 else 0
        hp_damage     = max(1, int((endroll - 100) * (0.42 + (weapon_df * 0.25)) * loc_df_mult) + crit_rank * 3)
        actual_damage = creature.take_damage(hp_damage)

        # Off-hand flare proc — tracked separately from main-hand counter
        off_flare = await resolve_flare(session, creature, off_weapon, "left")
        if off_flare:
            flare_dmg = off_flare.get("damage", 0)
            if flare_dmg > 0:
                creature.take_damage(flare_dmg)
        holy_flare_dmg = _holy_flare_damage(session, self.server)
        if holy_flare_dmg > 0:
            creature.take_damage(holy_flare_dmg)

        await session.send_line(colorize(roll_line, TextPresets.COMBAT_HIT))
        await session.send_line(colorize(
            f"    ... and hit for {actual_damage} points of damage!",
            TextPresets.COMBAT_HIT
        ))
        _requested_aim = aimed_location or getattr(session, "aimed_location", None)
        if _requested_aim:
            _body_type = getattr(creature, "body_type", "biped") or "biped"
            _valid_aim = resolve_aim(_body_type, _requested_aim)
            if not _valid_aim:
                await session.send_line(colorize(
                    f"    The {creature.name} has no {_requested_aim} to target - off-hand strikes at random!",
                    TextPresets.SYSTEM
                ))
            elif not aim_succeeded:
                await session.send_line(colorize(
                    f"    Your off-hand aim drifts - striking the {location} instead!",
                    TextPresets.SYSTEM
                ))
        await session.send_line(combat_damage(actual_damage, location))
        if crit_rank >= 1:
            old_sev = creature.wounds.get(location, 0)
            new_sev = creature.apply_wound(location, crit_rank)
            if new_sev > old_sev:
                impairment = creature.evaluate_combat_impairment(location, old_sev, new_sev)
                if impairment.get("dropped_weapon"):
                    await session.send_line(colorize(
                        f"    {creature.full_name.capitalize()} drops its weapon!",
                        TextPresets.COMBAT_HIT
                    ))
                if impairment.get("severed") and location in SEVERABLE_LOCATIONS:
                    await session.send_line(colorize(
                        f"    The off-hand strike severs {creature.full_name}'s {location}!",
                        TextPresets.COMBAT_HIT
                    ))
                if impairment.get("stance_shift"):
                    creature.stance = impairment["stance_shift"]
        if off_flare:
            await session.send_line(colorize(
                f"  {off_flare.get('attacker_msg', '')}",
                TextPresets.COMBAT_HIT
            ))
            if off_flare.get("damage", 0) > 0:
                await session.send_line(colorize(
                    f"  The flare deals {off_flare['damage']} additional points of damage!",
                    TextPresets.COMBAT_HIT
                ))
            off_room_msg = off_flare.get("room_msg", "")
            if off_room_msg:
                await self.server.world.broadcast_to_room(
                    session.current_room.id,
                    colorize(f"  {off_room_msg}", TextPresets.COMBAT_HIT),
                    exclude=[session],
                )
        if holy_flare_dmg > 0:
            await session.send_line(colorize(
                f"  Holy fire lashes out for {holy_flare_dmg} additional points of damage!",
                TextPresets.COMBAT_HIT
            ))

        if crit_rank > 0:
            crit_msgs = CRIT_MESSAGES.get(damage_type, CRIT_MESSAGES["slash"])
            await session.send_line(combat_crit(crit_rank, crit_msgs.get(crit_rank, "Critical hit!")))
            if crit_rank >= 3:
                try:
                    from server.core.engine.combat.status_effects import apply_bleed
                    apply_bleed(creature, crit_rank, attacker=session)
                except ImportError:
                    pass

        # Check if this off-hand blow killed it
        if creature.is_dead or crit_rank >= LETHAL_THRESHOLDS.get(location, 99):
            if not creature.is_dead:
                creature.take_damage(creature.health_current)
            await session.send_line(combat_death(creature.full_name.capitalize()))
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"  {creature.full_name.capitalize()} falls dead from the off-hand blow!",
                exclude=session
            )
            self.server.creatures.mark_dead(creature)
            session.target = None
            remaining = [
                c for c in self.server.creatures.get_creatures_in_room(session.current_room.id)
                if c.alive and c.aggressive and c is not creature
            ]
            if not remaining:
                _exit_combat(self.server, session)
                await session.send_line(colorize("The combat area is clear.", TextPresets.SYSTEM))
            if hasattr(self.server, 'experience'):
                from server.core.commands.player.party import award_party_kill_xp; await award_party_kill_xp(session, creature, self.server)

    async def creature_attacks_player(self, creature, session):
        """Resolve a creature attack against a player."""
        if not creature.can_act():
            return
        if maybe_auto_stand_before_attack(session, self.server):
            await session.send_line(colorize("  Combat Mobility snaps you back to your feet!", TextPresets.SYSTEM))

        # Dead players are untouchable — drop aggro and bail
        if getattr(session, "is_dead", False):
            creature.in_combat = False
            creature.target    = None
            return

        attack = creature.choose_attack()
        if not attack:
            return

        # Calculate creature AS
        creature_as = creature.get_melee_as(attack)
        stance_as_mod, _ = STANCE_MODS.get(creature.stance, (0, 0))
        creature_as += stance_as_mod

        # Calculate player DS with breakdown for miss flavor text
        player_ds, evade_ds, parry_ds, block_ds = self._calc_player_ds_breakdown(session)

        # Get attack verb and creature weapon name
        verb_first = attack.get("verb_first", "attacks you")
        verb_third = attack.get("verb_third", f"attacks {session.character_name}")
        attack_weapon = attack.get("weapon", None)  # e.g. "a rusty scimitar"

        # Set creature roundtime
        rt = attack.get("roundtime", 5)
        creature.set_roundtime(rt)

        # Players are always biped — use biped locations for incoming attacks
        location = self._random_body_location('biped')
        player_armor = _get_player_armor(session)
        player_asg = player_armor.get('armor_asg', 5) if player_armor else 5
        profile = _resolve_damage_profile(attack.get("damage_type", creature.damage_type), player_asg, None)
        damage_type = profile["damage_type"]
        avd = profile["avd"]

        # Roll
        d100 = random.randint(1, 100)
        endroll = d100 + creature_as - player_ds + avd

        # Creature display name with level
        creature_display = fmt_creature_name(creature.full_name_with_level.capitalize())

        # Check for player shield block (chance based on shield DS)
        # NOTE: Shield DS is already in player_ds above. This proc represents
        # a visible "you raised your shield" message on near-misses only,
        # NOT an additional damage reduction.
        player_shield = _get_player_shield(session)
        shield_blocked = False
        if player_shield and 95 < endroll <= 100:
            # The DS already prevented this hit. Show the shield flavor.
            shield_ds = player_shield.get('shield_ds', 0)
            block_chance = min(70, 30 + shield_ds * 2)
            if random.randint(1, 100) <= block_chance:
                shield_blocked = True

        # Build the attack swing line (GS4 format with creature weapon if any)
        if attack_weapon:
            swing_line = f"{creature_display} swings {attack_weapon} at you!"
        else:
            swing_line = f"{creature_display} {verb_first}!"

        # Roll line (GS4 format — full breakdown for creature attacks too)
        roll_line = (
            f"  AS: {'+' if creature_as >= 0 else ''}{creature_as} vs "
            f"DS: {'+' if player_ds >= 0 else ''}{player_ds} with "
            f"AvD: {'+' if avd >= 0 else ''}{avd} + "
            f"d100 roll: +{d100} = {'+' if endroll >= 0 else ''}{endroll}"
        )

        # Shield block
        if shield_blocked:
            shield_name = player_shield.get('short_name') or 'shield'
            set_reaction_trigger(session, "recent_block")
            await session.send_line(swing_line)
            await session.send_line(colorize(roll_line, TextPresets.COMBAT_MISS))
            await session.send_line(colorize(
                f"  You block the attack with your {shield_name}!",
                TextPresets.SYSTEM
            ))
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"{creature.full_name.capitalize()} attacks {session.character_name} but the blow is blocked!\n"
                f"  {roll_line}",
                exclude=session
            )
            return

        # Miss — show flavor text based on which DS component saved us
        if endroll <= 100:
            await session.send_line(swing_line.replace("!", " but misses!"))
            await session.send_line(colorize(roll_line, TextPresets.COMBAT_MISS))

            # Determine which defense primarily saved us
            weapon_equipped = bool(_get_player_weapon(session)[0])
            if block_ds >= parry_ds and block_ds >= evade_ds and block_ds > 0:
                shield = _get_player_shield(session)
                sname  = shield.get("short_name", "shield") if shield else "shield"
                set_reaction_trigger(session, "recent_block")
                await session.send_line(colorize(f"  You raise your {sname} and deflect the blow!", TextPresets.SYSTEM))
            elif parry_ds >= evade_ds and parry_ds > 0 and weapon_equipped:
                weapon, _ = _get_player_weapon(session)
                wname = weapon.get("short_name", "weapon") if weapon else "weapon"
                set_reaction_trigger(session, "recent_parry")
                await session.send_line(colorize(f"  You parry with your {wname}!", TextPresets.SYSTEM))
            elif evade_ds > 0:
                set_reaction_trigger(session, "recent_evade")
                dodge_msgs = [
                    "  You dodge out of the way!",
                    "  You sidestep the attack!",
                    "  You manage to evade the blow!",
                    "  You twist aside just in time!",
                ]
                await session.send_line(colorize(random.choice(dodge_msgs), TextPresets.SYSTEM))
            else:
                await session.send_line("  A clean miss.")

            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"{creature.full_name.capitalize()} {verb_third.replace('{target}', session.character_name)} but misses!\n"
                f"  {roll_line}",
                exclude=session
            )
            return

        # Hit!
        weapon_df = profile["df"]
        loc_df_mult = LOCATION_DAMAGE_MULT.get(location, 1.0)
        raw_damage = int((endroll - 100) * weapon_df * loc_df_mult)
        raw_damage = max(1, raw_damage)

        # Use player's actual worn armor ASG
        crit_divisor = max(1, int(CRIT_DIVISORS.get(player_asg, 6) * LOCATION_CRIT_DIV_MULT.get(location, 1.0)))
        crit_rank_max = min(9, raw_damage // crit_divisor)

        if crit_rank_max > 0:
            crit_rank_min = max(1, (crit_rank_max + 1) // 2)
            crit_rank = random.randint(crit_rank_min, crit_rank_max)
        else:
            crit_rank = 0

        hp_damage = max(1, int((endroll - 100) * (0.34 + (weapon_df * 0.20)) * loc_df_mult) + crit_rank * 2)
        hp_damage, ward_notes = _apply_player_wards(self.server, session, hp_damage)

        # Apply damage
        session.health_current = max(0, session.health_current - hp_damage)

        # ── Armor / shield elemental flare proc (defensive flare) ─────────────
        # When the player is hit, their worn armor or shield can flare back
        # against the attacker.  Counter-based same as weapon flares (every 5th
        # hit taken).  Flare damage is applied to the creature.
        armor_flare = await resolve_armor_flare(session, creature, player_armor, _get_player_shield(session))
        if armor_flare:
            af_dmg = armor_flare.get("damage", 0)
            if af_dmg > 0:
                creature.take_damage(af_dmg)

        # Output lines
        await session.send_line(swing_line)
        await session.send_line(colorize(roll_line, TextPresets.COMBAT_DAMAGE_TAKEN))
        await session.send_line(colorize(
            f"  ... {hp_damage} hit points of damage to your {location}!",
            TextPresets.COMBAT_DAMAGE_TAKEN
        ))
        for note in ward_notes:
            await session.send_line(colorize(f"  {note}", TextPresets.COMBAT_HIT))
        if armor_flare:
            await session.send_line(colorize(
                f"  {armor_flare.get('attacker_msg', '')}",
                TextPresets.COMBAT_HIT
            ))
            if armor_flare.get("damage", 0) > 0:
                await session.send_line(colorize(
                    f"  The flare deals {armor_flare['damage']} damage back to {creature.name}!",
                    TextPresets.COMBAT_HIT
                ))
            room_msg = armor_flare.get("room_msg", "")
            if room_msg:
                await self.server.world.broadcast_to_room(
                    session.current_room.id,
                    colorize(f"  {room_msg}", TextPresets.COMBAT_HIT),
                    exclude=[session],
                )

        # Show current HP inline so player never has to type HEALTH mid-fight
        hp_color = (TextPresets.HEALTH_FULL if session.health_current > session.health_max * 0.75
                    else TextPresets.WARNING if session.health_current > session.health_max * 0.25
                    else TextPresets.HEALTH_CRIT)
        await session.send_line(colorize(
            f"  Health: {session.health_current}/{session.health_max}",
            hp_color
        ))

        if crit_rank > 0:
            crit_msgs = CRIT_MESSAGES.get(damage_type, CRIT_MESSAGES["slash"])
            crit_msg = crit_msgs.get(crit_rank, "Critical hit!")
            await session.send_line(combat_crit(crit_rank, crit_msg))

            # ── Injury tracking ──────────────────────────────────────────────
            # Crits rank 3+ leave injuries that penalize AS/DS until healed
            if crit_rank >= 3:
                wb = getattr(self.server, 'wound_bridge', None)
                if wb and wb.available:
                    wound_result = wb.apply_wound(session, location, crit_rank)
                    new_rank = int(wound_result.get('new_rank', 0) or 0)
                    if new_rank > 0:
                        injury_severity = {1: "minor", 2: "moderate", 3: "major", 4: "severe", 5: "crippling"}
                        sev = injury_severity.get(new_rank, "serious")
                        await session.send_line(colorize(
                            f"  You have a {sev} injury to your {location}!",
                            TextPresets.COMBAT_DAMAGE_TAKEN
                        ))
                        if wound_result.get('did_bleed'):
                            await session.send_line(colorize(
                                "  You are bleeding!",
                                TextPresets.COMBAT_DAMAGE_TAKEN
                            ))
                        if getattr(self.server, "db", None) and getattr(session, "character_id", None):
                            try:
                                import asyncio as _asyncio
                                _asyncio.ensure_future(wb.save_wounds(session))
                            except Exception:
                                pass
                else:
                    if not hasattr(session, 'injuries') or session.injuries is None:
                        session.injuries = {}
                    existing = session.injuries.get(location, 0)
                    session.injuries[location] = min(5, max(existing, crit_rank // 2))
                    injury_severity = {1: "minor", 2: "moderate", 3: "major", 4: "severe", 5: "crippling"}
                    sev = injury_severity.get(session.injuries[location], "serious")
                    await session.send_line(colorize(
                        f"  You have a {sev} injury to your {location}!",
                        TextPresets.COMBAT_DAMAGE_TAKEN
                    ))
                    # Apply bleed from serious wounds
                    try:
                        from server.core.engine.combat.status_effects import apply_bleed
                        apply_bleed(session, crit_rank)
                        if crit_rank >= 4:
                            await session.send_line(colorize(
                                "  You are bleeding!",
                                TextPresets.COMBAT_DAMAGE_TAKEN
                            ))
                    except ImportError:
                        pass

            # ── Player stun on high crits ─────────────────────────────────────
            if crit_rank >= 4:
                import time as _time
                stun_rt = crit_rank
                stun_end = _time.time() + stun_rt
                current_rt = getattr(session, '_roundtime_end', 0)
                if stun_end > current_rt:
                    session._roundtime_end = stun_end
                await session.send_line(colorize(
                    f"  You are stunned for {stun_rt} seconds!",
                    TextPresets.WARNING
                ))

        # Health warnings
        if session.health_current <= 0:
            await session.send_line(colorize(
                "  You have been slain!",
                TextPresets.COMBAT_DEATH
            ))
        elif session.health_current < session.health_max * 0.25:
            await session.send_line(colorize(
                f"  Your health is critical! ({session.health_current}/{session.health_max})",
                TextPresets.HEALTH_CRIT
            ))

        # Broadcast full roll details to observers
        crit_obs = f"  Crit rank {crit_rank}!" if crit_rank > 0 else ""
        await self.server.world.broadcast_to_room(
            session.current_room.id,
            f"{creature.full_name.capitalize()} {verb_third.replace('{target}', session.character_name)} and hits!\n"
            f"  {roll_line}\n"
            f"  {hp_damage} points of damage to {session.character_name}'s {location}.{chr(10) + crit_obs if crit_obs else ''}",
            exclude=session
        )

        # Save state
        if self.server.db and session.character_id:
            self.server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver
            )

        # Death check
        if session.health_current <= 0:
            await self._player_death(session, creature)

        # Keep combat
        creature.in_combat = True
        creature.target = session
        session.in_combat = True
        session.target = creature

    async def _player_death(self, session, killer):
        """Hand off to DeathManager for the full death flow."""
        if hasattr(self.server, 'death'):
            await self.server.death.handle_player_death(session, killer=killer)
        else:
            # Fallback if death manager not yet registered
            _exit_combat(self.server, session)
            session.target         = None
            session.health_current = max(1, session.health_max // 2)
            session.position       = "standing"
            await session.send_line(colorize(
                "  (Death system not loaded — emergency revive applied.)",
                TextPresets.WARNING
            ))
            if self.server.db and session.character_id:
                self.server.db.save_character_resources(
                    session.character_id,
                    session.health_current, session.mana_current,
                    session.spirit_current, session.stamina_current,
                    session.silver
                )

    # ================================================================
    # Helpers
    # ================================================================
    # ── Stance weapon-skill multipliers (wiki: 100% offensive → 50% defensive) ──
    # Stance percent = defensiveness (OFF=0%, ADV=20%, FOR=40%, NEU=60%, GUA=80%, DEF=100%)
    # Weapon skill applied to AS = 1.0 - (stance_pct / 2)
    _STANCE_WEAPON_PCT = {
        "offensive": 1.00,
        "advance":   0.90,
        "forward":   0.80,
        "neutral":   0.70,
        "guarded":   0.60,
        "defensive": 0.50,
    }

    def _calc_player_as(self, session):
        """GS4 canonical melee AS (wiki: Attack_strength):
            Melee AS = STR Bonus + Weapon Skill Bonus + [CM Ranks / 2]
                     + Weapon Enchantment + Modifiers
        Stance multiplies the WHOLE total: 100% (OFF) → 50% (DEF).
        No level base. DEX is not part of melee AS.
        Unarmed routes to _calc_player_uaf — do not call this bare-handed.
        """
        weapon, _ = _get_player_weapon(session)

        buffs = _buff_totals(session, self.server)
        cman_passive = get_passive_combat_mods(session, self.server)
        cman_temp = get_temp_combat_bonus_totals(session)
        status_as_mod, _status_ds_mod, _status_evade_pen, _status_parry_pen, _status_block_pen = _status_combat_mods(self.server, session)
        str_bonus = (
            (
                session.stat_strength
                + int(buffs.get("strength_bonus", 0) or 0)
                + int(cman_temp.get("strength_bonus", 0) or 0)
                - int(buffs.get("strength_penalty", 0) or 0)
            )
            - 50
        ) // 2
        cm_bonus  = _sr(session, SKILL_COMBAT_MANEUVERS) // 2

        if weapon:
            skill_bonus  = _sb(session, _weapon_skill_id(weapon))
            raw_enc      = weapon.get('enchant_bonus', 0) or 0
            enchant      = _calc_effective_enchant(session.level, raw_enc)
            attack_bonus = weapon.get('attack_bonus', 0)
        else:
            skill_bonus  = 0
            enchant      = 0
            attack_bonus = 0

        # Raw AS — all components, before stance
        raw_as = str_bonus + skill_bonus + cm_bonus + enchant + attack_bonus
        raw_as += int(buffs.get("as_bonus", 0) or 0)
        raw_as -= int(buffs.get("as_penalty", 0) or 0)
        raw_as += int(cman_passive.get("as_bonus", 0) or 0)
        raw_as += int(cman_temp.get("as_bonus", 0) or 0)

        # Action penalty from armor — Armor Use ranks reduce it
        # GS4: full penalty at 0 Armor Use ranks, 0 penalty at sufficient ranks
        armor = _get_player_armor(session)
        if armor:
            base_penalty = int(armor.get("action_penalty", 0) or 0)
            if base_penalty > 0:
                au_ranks     = _sr(session, SKILL_ARMOR_USE)
                # Each rank reduces penalty by 0.5, capped at full removal
                au_reduction = min(base_penalty, int(au_ranks * 0.5))
                raw_as      -= (base_penalty - au_reduction)

        # Feint debuff: creature has a temporary DS reduction stored on it
        # (Applied to creature DS in player_attacks_creature, not here)

        # Stance multiplies the entire AS value (wiki: 100% OFF → 50% DEF)
        stance_mult = self._STANCE_WEAPON_PCT.get(session.stance, 0.70)
        base = int(raw_as * stance_mult)

        # Injury penalties (post-stance)
        injuries = getattr(session, 'injuries', {})
        for loc, severity in injuries.items():
            if loc in ('right_arm', 'left_arm', 'right_hand', 'left_hand') and severity >= 3:
                base -= severity * 3

        base += int(status_as_mod or 0)

        base = int(base * getattr(session, 'death_stat_mult', 1.0))

        # Encumbrance AS penalty (applies after all other modifiers)
        base += encumbrance_as_ds_penalty(session)

        return base

    def _calc_player_uaf(self, session):
        """Calculate player Unarmed Attack Factor (UAF) for UCS combat.

        Wiki formula:
          UAF = (Brawling Ranks × 2)
              + trunc(CM Ranks / 2)
              + trunc(STR bonus / 2)
              + trunc(AGI bonus / 2)
              + glove/boot enchant bonus
              + trunc(avg held UCS weapon enchant / 2)

        UAF is NOT affected by stance (stance affects MM instead).
        """
        cman_temp = get_temp_combat_bonus_totals(session)
        status_as_mod, _status_ds_mod, _status_evade_pen, _status_parry_pen, _status_block_pen = _status_combat_mods(self.server, session)
        brawling_ranks = _sr(session, SKILL_BRAWLING)
        cm_ranks       = _sr(session, SKILL_COMBAT_MANEUVERS)
        str_bonus      = ((getattr(session, 'stat_strength',  50) + int(cman_temp.get("strength_bonus", 0) or 0)) - 50) // 2
        agi_bonus      = ((getattr(session, 'stat_agility',   50) + int(cman_temp.get("agility_bonus", 0) or 0)) - 50) // 2

        uaf = (brawling_ranks * 2) + (cm_ranks // 2) + (str_bonus // 2) + (agi_bonus // 2)
        uaf += int(cman_temp.get("as_bonus", 0) or 0)

        # Glove enchant bonus (worn UCS hand equipment)
        for item in getattr(session, 'inventory', []):
            if item.get('slot') in ('gloves', 'hands') and item.get('ucs_compatible'):
                uaf += item.get('enchant_bonus', 0)

        # Held UCS brawling weapon enchant: avg / 2
        held_enc = []
        for hand in ('right_hand', 'left_hand'):
            item = getattr(session, hand, None)
            if item and item.get('ucs_compatible') and item.get('enchant_bonus', 0):
                held_enc.append(item['enchant_bonus'])
        if held_enc:
            avg_enc = sum(held_enc) // len(held_enc)
            uaf += avg_enc // 2

        # Injury penalties to hands reduce UAF
        injuries = getattr(session, 'injuries', {})
        for loc, severity in injuries.items():
            if loc in ('right_arm', 'left_arm', 'right_hand', 'left_hand') and severity >= 3:
                uaf -= severity * 2

        uaf += int(status_as_mod or 0)

        uaf = int(uaf * getattr(session, 'death_stat_mult', 1.0))
        return max(1, uaf)

    def _calc_player_ds(self, session):
        """Wrapper — returns just total DS for backward compat."""
        total, _, _, _ = self._calc_player_ds_breakdown(session)
        return total

    def _calc_player_ds_breakdown(self, session):
        """GS4 canonical DS breakdown → (total, evade_ds, parry_ds, block_ds)."""
        buffs = _buff_totals(session, self.server)
        cman_passive = get_passive_combat_mods(session, self.server)
        cman_temp = get_temp_combat_bonus_totals(session)
        _status_as_mod, status_ds_mod, status_evade_pen, status_parry_pen, status_block_pen = _status_combat_mods(self.server, session)
        str_bonus = ((session.stat_strength + int(buffs.get("strength_bonus", 0) or 0) - int(buffs.get("strength_penalty", 0) or 0)) - 50) // 2
        dex_bonus = ((session.stat_dexterity + int(cman_temp.get("dexterity_bonus", 0) or 0)) - 50) // 2
        agi_bonus = ((session.stat_agility + int(cman_temp.get("agility_bonus", 0) or 0)) - 50) // 2
        int_bonus = ((session.stat_intuition + int(cman_temp.get("intuition_bonus", 0) or 0)) - 50) // 2

        def_pct = {
            "offensive": 0.0, "advance": 0.2, "forward": 0.4,
            "neutral":   0.6, "guarded": 0.8, "defensive": 1.0,
        }.get(session.stance, 0.6)
        stance = session.stance

        # ── Evade DS ──────────────────────────────────────────────────────
        evade_base = _sr(session, SKILL_DODGING) + agi_bonus + int(int_bonus / 4)
        evade_base += int(buffs.get("dodge_bonus", 0) or 0)

        armor = _get_player_armor(session)
        asg   = armor.get("armor_asg", 1) if armor else 1
        armor_override = int(buffs.get("armor_asg_override", 0) or 0)
        if armor_override > asg:
            asg = armor_override

        BASE_HINDRANCE = {
            1: 1.00, 2: 1.00, 3: 1.00, 4: 1.00,
            5: 0.98, 6: 0.97, 7: 0.96, 8: 0.94,
            9: 0.92, 10: 0.88, 11: 0.84, 12: 0.80,
            13: 0.75, 14: 0.70, 15: 0.65, 16: 0.60,
            17: 0.55, 18: 0.50, 19: 0.45, 20: 0.40,
        }
        base_hind = BASE_HINDRANCE.get(asg, 1.0)
        au_ranks  = _sr(session, SKILL_ARMOR_USE)
        max_ranks = max(1, int((1.0 - base_hind) * 500))
        au_reduc  = min(au_ranks / max_ranks, 1.0 - base_hind)
        hindrance = min(1.0, base_hind + au_reduc)

        shield = _get_player_shield(session)
        if shield:
            s_type    = shield.get("shield_type", "medium")
            s_factor  = {"small": 0.78, "medium": 0.70, "large": 0.62, "tower": 0.54}.get(s_type, 0.70)
            s_penalty = {"small": 0, "medium": 0, "large": 5, "tower": 10}.get(s_type, 0)
        else:
            s_type    = "medium"
            s_factor  = 1.0
            s_penalty = 0

        evade_stance = 0.75 + (def_pct * 0.25)
        evade_ds = int((int(int(evade_base * hindrance) * s_factor) - s_penalty) * evade_stance)
        evade_ds += int(cman_passive.get("ds_bonus", 0) or 0) // 3
        evade_ds += int(cman_temp.get("ds_bonus", 0) or 0) // 3
        evade_ds = int(
            evade_ds * (
                max(
                    0.0,
                    1.0
                    + (
                        int(cman_passive.get("evade_pct_bonus", 0) or 0)
                        + int(cman_temp.get("evade_pct_bonus", 0) or 0)
                        - int(status_evade_pen or 0)
                    ) / 100.0
                )
            )
        )
        evade_ds = max(0, evade_ds)

        # ── Parry DS ──────────────────────────────────────────────────────
        ohw_mod     = {"offensive": 0.20, "advance": 0.30, "forward": 0.40,
                       "neutral": 0.50, "guarded": 0.60, "defensive": 0.70}
        thw_mod     = {"offensive": 0.30, "advance": 0.45, "forward": 0.60,
                       "neutral": 0.75, "guarded": 0.90, "defensive": 1.05}
        parry_bonus = {"offensive": 0, "advance": 10, "forward": 20,
                       "neutral": 30, "guarded": 40, "defensive": 50}

        weapon, _ = _get_player_weapon(session)
        parry_ds  = 0
        if weapon:
            w_ranks = _sr(session, _weapon_skill_id(weapon))
            w_enc   = weapon.get("enchant_bonus", 0) or 0
            w_cat   = (weapon.get("weapon_category", "edged") or "edged").lower()
            if w_cat == "twohanded":
                p_base = w_ranks + int(str_bonus / 4) + int(dex_bonus / 4) + w_enc
                p_mod  = thw_mod.get(stance, 0.75)
            else:
                p_base = w_ranks + int(str_bonus / 4) + int(dex_bonus / 4) + int(w_enc / 2)
                p_mod  = ohw_mod.get(stance, 0.50)
            parry_ds = int(p_base * p_mod) + parry_bonus.get(stance, 30)
        else:
            brawl = _sr(session, SKILL_BRAWLING)
            if brawl > 0:
                p_base   = brawl + int(str_bonus / 4) + int(dex_bonus / 4)
                parry_ds = int(p_base * ohw_mod.get(stance, 0.50)) + parry_bonus.get(stance, 30)
        parry_ds = int(
            parry_ds * (
                max(
                    0.0,
                    1.0
                    + (
                        int(cman_passive.get("parry_pct_bonus", 0) or 0)
                        + int(cman_temp.get("parry_pct_bonus", 0) or 0)
                        - int(status_parry_pen or 0)
                    ) / 100.0
                )
            )
        )

        # ── Block DS ──────────────────────────────────────────────────────
        block_ds = 0
        if shield:
            sh_ranks     = _sr(session, SKILL_SHIELD_USE)
            block_base   = sh_ranks + int(str_bonus / 4) + int(dex_bonus / 4)
            block_stance = 0.5 + (def_pct * 0.5)
            size_mod     = {"small": -0.15, "medium": 0.0, "large": 0.15, "tower": 0.30}.get(s_type, 0.0)
            size_bonus   = {"small": 15, "medium": 20, "large": 25, "tower": 30}.get(s_type, 20)
            sh_enc       = _calc_effective_enchant(session.level, shield.get("enchant_bonus", 0) or 0)
            block_ds     = int(int(block_base * block_stance) * (1.0 + size_mod)) + size_bonus + sh_enc
            block_ds     = max(0, block_ds)
        block_ds = int(
            block_ds * (
                max(
                    0.0,
                    1.0
                    + (
                        int(cman_passive.get("block_pct_bonus", 0) or 0)
                        + int(cman_temp.get("block_pct_bonus", 0) or 0)
                        - int(status_block_pen or 0)
                    ) / 100.0
                )
            )
        )

        # ── Generic DS (status + MOC) ──────────────────────────────────────
        generic_ds = 0
        for loc, severity in getattr(session, "injuries", {}).items():
            if severity >= 3:
                generic_ds -= severity * 2

        # MOC: each extra attacker beyond first = -25 DS offset by MOC ranks
        try:
            room_id   = session.current_room.id if session.current_room else None
            if room_id is not None:
                attackers = [
                    c for c in self.server.creatures.get_creatures_in_room(room_id)
                    if c.alive and getattr(c, "in_combat", False) and c.target is session
                ]
                extra = max(0, len(attackers) - 1)
                if extra > 0:
                    moc_ranks = _sr(session, SKILL_MOC)
                    penalty   = extra * 25
                    offset    = min(moc_ranks, penalty)
                    generic_ds -= (penalty - offset)
        except Exception:
            pass

        # Feint debuff from player on a creature just saved by DS (applied opposite direction —
        # feint is stored on creature, not session; handled in player_attacks_creature)

        total = evade_ds + parry_ds + block_ds + generic_ds
        total += int(buffs.get("ds", 0) or 0)
        total -= int(buffs.get("ds_penalty", 0) or 0)
        total += int(status_ds_mod or 0)
        total += int(cman_passive.get("ds_bonus", 0) or 0)
        total += int(cman_temp.get("ds_bonus", 0) or 0)
        total = int(total * getattr(session, "death_stat_mult", 1.0))

        # Encumbrance DS penalty (applies after death_stat_mult)
        total += encumbrance_as_ds_penalty(session)
        total = max(0, total)

        return total, evade_ds, parry_ds, block_ds

    def _random_body_location(self, body_type: str = "biped") -> str:
        """Pick a weighted-random hit location for a creature of the given body_type.
        Delegates to body_types_loader which reads scripts/data/body_types.lua.
        """
        return random_location(body_type)

    def _resolve_hit_location(self, session, creature, aimed_location_override=None, hidden_ambush=False) -> tuple[str, bool]:
        """
        Determine the final hit location for a player attack on a creature.

        Returns (location: str, aimed_succeeded: bool).
          aimed_succeeded=True  → player hit their intended spot
          aimed_succeeded=False → aim drifted to a random location

        Priority order:
          1. aimed_location_override  (passed explicitly, e.g. from AMBUSH cmd)
          2. session.aimed_location   (persistent AIM preference)
          3. Random weighted by creature body_type

        For aimed attacks an aim-success roll is made from the Lua-driven
        ambush config:
          hidden ambush  -> Ambush bonus only
          open aiming    -> Ambush bonus and Combat Maneuvers equally

        If the roll fails the attack drifts to a random location on the
        creature instead of the intended spot.  This preserves the GS4
        mechanic that you're never guaranteed to hit exactly where you aim.
        """
        body_type = getattr(creature, "body_type", "biped") or "biped"

        # Determine requested aim (override wins over session preference)
        requested = aimed_location_override or getattr(session, "aimed_location", None)

        if not requested:
            return self._random_body_location(body_type), False

        # Resolve the requested location against this creature's body type
        canonical = resolve_aim(body_type, requested)

        if not canonical:
            # Creature doesn't have this location (e.g. "right hand" on a snake)
            # Silently drift to random — the attack message will note the miss
            return self._random_body_location(body_type), False

        cfg = self._get_ambush_cfg()
        hidden_cfg = cfg.get("hidden", {}) or {}
        open_cfg = cfg.get("open_aim", {}) or {}
        ambush_bonus = self._get_ambush_skill_bonus(session)
        cm_bonus = self._get_ambush_cm_bonus(session)

        # Aim difficulty for this location on this body type
        locs = get_locations(body_type)
        loc_data = locs.get(canonical, {})
        aim_penalty = loc_data.get("aim_penalty", 10)

        if hidden_ambush:
            roll_bonus = int(ambush_bonus * float(hidden_cfg.get("aim_bonus_mult", 0.25) or 0.25))
            threshold = int(
                aim_penalty
                + (getattr(creature, "level", 1) * float(hidden_cfg.get("threshold_level_mult", 2.0) or 2.0))
                + float(hidden_cfg.get("threshold_flat", 0) or 0)
            )
        else:
            roll_bonus = int(ambush_bonus * float(open_cfg.get("ambush_bonus_mult", 0.25) or 0.25))
            roll_bonus += int(cm_bonus * float(open_cfg.get("cm_bonus_mult", 0.25) or 0.25))
            threshold = int(
                aim_penalty
                + (getattr(creature, "level", 1) * float(open_cfg.get("threshold_level_mult", 2.0) or 2.0))
                + float(open_cfg.get("threshold_flat", 0) or 0)
            )
        roll = random.randint(1, 100) + roll_bonus

        if roll >= threshold:
            return canonical, True
        else:
            # Drift — random location, not the aimed one
            return self._random_body_location(body_type), False
