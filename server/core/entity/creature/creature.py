"""
Creature - A living creature/monster in the game world.
Each creature instance is a single spawned mob with its own HP, position, etc.
Creature templates (stats, attacks) are defined in creature_data.py and loaded
from the database or Lua scripts.
"""

import time
import random
import logging
from server.core.engine.combat.status_effects import get_combat_mods as get_status_combat_mods
from server.core.scripting.loaders.body_types_loader import get_locations

log = logging.getLogger(__name__)


class Creature:
    """A single creature instance in the game world."""

    _next_id = 10000  # Creature IDs start at 10000 to avoid collision with players

    def __init__(self, template):
        """
        Create a creature from a template dict.
        Template keys: name, article, level, hp, as_melee, ds_melee, ds_ranged,
                       ds_bolt, td, udf, armor_asg, cva, attacks, treasure,
                       skin, description, body_type, family, damage_type,
                       spawn_rooms, wander_rooms, respawn_time
        """
        self.id = Creature._next_id
        Creature._next_id += 1

        # Identity
        self.template_id = template.get("template_id", "unknown")
        self.name = template.get("name", "an unknown creature")
        self.article = template.get("article", "a")  # "a", "an", "the"
        self.level = template.get("level", 1)
        self.body_type = template.get("body_type", "biped")
        self.family = template.get("family", "")
        self.classification = template.get("classification", "living")
        self.description = template.get("description", "You see nothing unusual.")

        # Combat stats (from template)
        self.health_max = template.get("hp", 28)
        self.health_current = self.health_max
        self.as_melee = template.get("as_melee", 40)
        self.ds_melee = template.get("ds_melee", 20)
        self.ds_ranged = template.get("ds_ranged", 20)
        self.ds_bolt = template.get("ds_bolt", 20)
        self.td = template.get("td", 3)  # Target defense (vs magic)
        self.td_spiritual = template.get("td_spiritual", self.td)
        self.td_elemental = template.get("td_elemental", self.td)
        self.udf = template.get("udf", 14)
        self.armor_asg = template.get("armor_asg", 1)  # Armor skin group
        self.cva = template.get("cva", 0)  # Creature vs Armor modifier
        self.damage_type = template.get("damage_type", "slash")  # primary damage type

        # Attacks: list of {name, as, damage_type, verb_first, verb_third, roundtime}
        self.attacks = template.get("attacks", [
            {"name": "bite", "as": self.as_melee, "damage_type": "puncture",
             "verb_first": "bites at you", "verb_third": "bites at {target}", "roundtime": 5}
        ])

        # Treasure
        self.treasure = template.get("treasure", {
            "coins": False, "gems": False, "magic": False, "boxes": False
        })
        self.skin = template.get("skin", None)
        self.special_loot = list(template.get("special_loot", []) or [])
        self.stolen_items = list(template.get("stolen_items", []) or [])
        self.skinned = False
        self.searched = False
        self.spells = list(template.get("spells", []) or [])
        self.abilities = list(template.get("abilities", []) or [])
        self.immune = list(template.get("immune", []) or [])
        self.resist = list(template.get("resist", []) or [])
        self.skills = list(template.get("skills", []) or [])
        self.preferred_stance = (template.get("preferred_stance") or None)
        self.stance_profile = (template.get("stance_profile") or None)
        self.flags = list(template.get("flags", []) or [])
        self.traits = list(template.get("traits", []) or [])
        self.keywords = list(template.get("keywords", []) or [])
        self.movement_modes = list(template.get("movement_modes", []) or [])
        self.movement_tags = list(template.get("movement_tags", []) or [])
        self.flying = bool(template.get("flying", False))
        self.airborne = bool(template.get("airborne", False))
        self.levitating = bool(template.get("levitating", False))
        self.hovering = bool(template.get("hovering", False))

        # State
        self.current_room_id = 0
        self.alive = True
        self.in_combat = False
        self.target = None  # session of player it's fighting
        self.stance = "neutral"
        self.roundtime_end = 0
        self.spawn_time = time.time()
        self.death_time = 0

        # Spawning config
        self.spawn_rooms = template.get("spawn_rooms", [])
        self.wander_rooms = template.get("wander_rooms", [])
        self.respawn_time = template.get("respawn_time", 60)

        # Behavior
        self.aggressive = template.get("aggressive", True)
        self.wander_chance = template.get("wander_chance", 0.1)
        self.pursue_chance = template.get("pursue_chance", 0.3)

        # Status effects
        self.stunned_until = 0
        self.prone = False
        self.immobilized = False
        self.ai_as_bonus = 0
        self.ai_ds_bonus = 0
        self._forced_attack = None
        self._last_spell_time = 0.0
        self._ability_cooldowns: dict = {}
        self._temp_bonuses: dict = {}
        self._temp_states: dict = {}

        # ── Wound tracking (GS4 wiki: wounds reduce AS/DS per location) ──────
        # wounds = {location: severity}  severity 1-5 (minor→crippling)
        # GS4 crit ranks 1-2=minor(1), 3-4=moderate(2), 5-6=major(3), 7-8=severe(4), 9=crippling(5)
        self.wounds: dict = {}
        self.status_effects: dict = {}
        self.disarmed = False
        self.severed_locations: set[str] = set()
        self._stance_tick_counter = 0

    @property
    def full_name(self):
        """Return full name with article: 'a fanged rodent'."""
        return self.article + " " + self.name

    @property
    def full_name_with_level(self):
        """Return name with level for combat display: 'a fanged rodent [Level 1]'."""
        return self.article + " " + self.name + " [Level " + str(self.level) + "]"

    @property
    def is_dead(self):
        return not self.alive or self.health_current <= 0

    @property
    def is_stunned(self):
        if time.time() < self.stunned_until:
            return True
        stunned = getattr(self, "status_effects", {}) or {}
        effect = stunned.get("stunned")
        if not effect:
            return False
        expires = getattr(effect, "expires", 0)
        return expires < 0 or time.time() < expires

    def get_roundtime(self):
        remaining = self.roundtime_end - time.time()
        return max(0, remaining)

    def set_roundtime(self, seconds):
        self.roundtime_end = time.time() + seconds

    def take_damage(self, amount):
        """Apply damage to the creature. Returns actual damage dealt."""
        actual = min(amount, self.health_current)
        self.health_current -= actual
        if self.health_current <= 0:
            self.health_current = 0
            self.alive = False
            self.death_time = time.time()
            self.in_combat = False
            self.target = None
            self.wounds = {}          # clear wounds on death
            self.status_effects = {}  # clear effects on death
        return actual

    def heal(self, amount):
        """Heal the creature."""
        self.health_current = min(self.health_current + amount, self.health_max)

    def choose_attack(self):
        """Pick a random attack from available attacks."""
        if self._forced_attack:
            attack = dict(self._forced_attack)
            self._forced_attack = None
            return attack
        if not self.attacks:
            return None
        usable = [atk for atk in self.attacks if self._attack_is_usable(atk)]
        if usable:
            return random.choice(usable)
        if self.attacks:
            return self._fallback_unarmed_attack()
        return None

    def _fallback_unarmed_attack(self):
        """Fallback when a creature loses effective weapon use."""
        body_type = (getattr(self, "body_type", "biped") or "biped").lower()
        if body_type in ("quadruped", "avian", "arachnid", "insectoid"):
            return {
                "name": "claw",
                "as": max(5, int(self.as_melee * 0.55)),
                "damage_type": "slash",
                "verb_first": "lashes at you desperately",
                "verb_third": "lashes at {target} desperately",
                "roundtime": 5,
            }
        if body_type == "ophidian":
            return {
                "name": "bite",
                "as": max(5, int(self.as_melee * 0.60)),
                "damage_type": "puncture",
                "verb_first": "snaps at you wildly",
                "verb_third": "snaps at {target} wildly",
                "roundtime": 5,
            }
        return {
            "name": "kick",
            "as": max(5, int(self.as_melee * 0.45)),
            "damage_type": "crush",
            "verb_first": "kicks at you awkwardly",
            "verb_third": "kicks at {target} awkwardly",
            "roundtime": 5,
        }

    def _attack_is_armed(self, attack: dict) -> bool:
        """Best-effort classification for attacks that rely on a hand/weapon limb."""
        name = str((attack or {}).get("name", "") or "").lower().strip()
        armed = {
            "broadsword", "dagger", "scimitar", "longsword", "two_handed_sword",
            "morning_star", "mace", "military_pick", "spear", "handaxe", "staff",
            "short_sword", "rapier", "falchion", "battle_axe", "war_hammer",
            "club", "quarterstaff", "katana", "halberd", "trident", "naginata",
            "jeddart_axe", "awl_pike", "lance", "pick", "hammer", "blackjack",
        }
        return name in armed

    def _attack_is_usable(self, attack: dict) -> bool:
        """Filter attacks that are no longer viable due to limb loss."""
        if not attack:
            return False
        name = str(attack.get("name", "") or "").lower()
        if self._attack_is_armed(attack):
            if self.disarmed or self.location_disabled("right hand") or self.location_disabled("right arm"):
                return False
        if name in {"kick", "stomp", "trample", "charge"}:
            if self.location_disabled("right leg") and self.location_disabled("left leg"):
                return False
        return True

    def location_disabled(self, location: str) -> bool:
        sev = int((self.wounds or {}).get(location, 0) or 0)
        return sev >= 4

    def location_severed(self, location: str) -> bool:
        sev = int((self.wounds or {}).get(location, 0) or 0)
        return sev >= 5

    def get_melee_as(self, attack=None):
        """Get attack strength, degraded by wounds/HP and modified by statuses."""
        base = attack.get("as", self.as_melee) if attack else self.as_melee
        status_as_mod, _status_ds_mod = get_status_combat_mods(self)

        # ── Wound penalties — body-type-aware ────────────────────────────────
        # We map location groups to penalty multipliers so that quadrupeds,
        # ophidians, etc. all have correct wound degradation.
        # Groups: AS_ATTACK = primary weapon limbs, AS_BALANCE = torso/head
        penalty = 0
        bt = getattr(self, "body_type", "biped") or "biped"
        locs = get_locations(bt)

        # Head wound: concentration/coordination lost (-5/severity)
        penalty += self.wounds.get("head", 0) * 5

        # Primary attack limbs (right arm / right foreleg / body for ophidians)
        # These are the locations that most directly affect the attack delivery
        AS_PRIMARY = {
            "biped":     [("right arm", 8), ("right hand", 10), ("left arm", 3)],
            "quadruped": [("right foreleg", 8), ("left foreleg", 4)],
            "ophidian":  [("body", 4), ("neck", 6)],
            "hybrid":    [("right arm", 8), ("right hand", 10), ("left arm", 3)],
            "avian":     [("right wing", 7), ("left wing", 4), ("right talon", 9)],
            "arachnid":  [("cephalothorax", 6)],
            "insectoid": [("thorax", 5), ("right foreleg", 6)],
        }
        for loc, mult in AS_PRIMARY.get(bt, AS_PRIMARY["biped"]):
            penalty += self.wounds.get(loc, 0) * mult

        # Chest/torso wound: harder to swing powerfully (-3/severity)
        for torso_loc in ("chest", "thorax", "body"):
            if torso_loc in locs:
                penalty += self.wounds.get(torso_loc, 0) * 3
                break

        if attack and self._attack_is_armed(attack):
            if self.location_disabled("right hand") or self.location_disabled("right arm"):
                penalty += 55
            if self.location_severed("right hand") or self.location_severed("right arm"):
                penalty += 35
        if self.location_disabled("left hand") or self.location_disabled("left arm"):
            penalty += 10
        if self.location_disabled("right leg") or self.location_disabled("left leg"):
            penalty += 8

        # ── HP-based degradation (GS4 wiki: creatures fight worse when hurt) ─
        if self.health_max > 0:
            hp_pct = self.health_current / self.health_max
            if hp_pct < 0.75:
                hp_penalty = int((0.75 - hp_pct) / 0.75 * 40)
                penalty += hp_penalty

        return max(
            0,
            base
            - penalty
            + int(status_as_mod or 0)
            + int(getattr(self, "ai_as_bonus", 0) or 0)
            + int(self.get_temp_as_bonus()),
        )

    def get_melee_ds(self):
        """Get defensive strength, degraded by wounds/HP and modified by statuses."""
        ds = self.ds_melee
        _status_as_mod, status_ds_mod = get_status_combat_mods(self)

        # Stance modifier (unchanged)
        if self.stance == "defensive":
            ds += 25
        elif self.stance == "guarded":
            ds += 15
        elif self.stance == "advance":
            ds -= 10
        elif self.stance == "offensive":
            ds -= 20

        # ── Wound penalties — body-type-aware ────────────────────────────────
        penalty = 0
        bt = getattr(self, "body_type", "biped") or "biped"
        locs = get_locations(bt)

        # Head wound: disorientation (-4/severity for all types)
        penalty += self.wounds.get("head", 0) * 4

        # Primary torso wound: hardest to defend with torso injured (-8/severity)
        for torso_loc in ("chest", "thorax", "body"):
            if torso_loc in locs:
                penalty += self.wounds.get(torso_loc, 0) * 8
                break

        # Abdomen/belly wound: balance and movement impaired (-6/severity)
        for abd_loc in ("abdomen", "belly"):
            if abd_loc in locs:
                penalty += self.wounds.get(abd_loc, 0) * 6
                break

        # Defensive limb groups — parrying/shielding limb wounds hurt DS
        DS_DEFEND = {
            "biped":     [("left arm", 7), ("left hand", 9),
                          ("right leg", 4), ("left leg", 4)],
            "quadruped": [("left foreleg", 7), ("right foreleg", 4),
                          ("left hindleg", 5), ("right hindleg", 5)],
            "ophidian":  [("tail", 4), ("neck", 5)],
            "hybrid":    [("left arm", 7), ("left hand", 9),
                          ("left wing", 5), ("right wing", 4),
                          ("right leg", 4), ("left leg", 4)],
            "avian":     [("left wing", 7), ("right wing", 5),
                          ("left talon", 5), ("right talon", 4)],
            "arachnid":  [("leg 1", 4), ("leg 2", 4),
                          ("leg 3", 4), ("leg 4", 4)],
            "insectoid": [("left foreleg", 5), ("right foreleg", 4),
                          ("left midleg", 3), ("right midleg", 3)],
        }
        for loc, mult in DS_DEFEND.get(bt, DS_DEFEND["biped"]):
            penalty += self.wounds.get(loc, 0) * mult

        if self.location_disabled("right leg") or self.location_disabled("left leg"):
            penalty += 15
        if self.location_disabled("right hand") or self.location_disabled("left hand"):
            penalty += 8

        # ── HP-based degradation ──────────────────────────────────────────────
        if self.health_max > 0:
            hp_pct = self.health_current / self.health_max
            if hp_pct < 0.75:
                hp_penalty = int((0.75 - hp_pct) / 0.75 * 50)
                penalty += hp_penalty

        return max(
            0,
            ds
            - penalty
            + int(status_ds_mod or 0)
            + int(getattr(self, "ai_ds_bonus", 0) or 0)
            + int(self.get_temp_ds_bonus()),
        )

    def get_ranged_ds(self) -> int:
        """Get ranged defensive strength with status modifiers applied."""
        _status_as_mod, status_ds_mod = get_status_combat_mods(self)
        return max(0, int(getattr(self, "ds_ranged", self.ds_melee) or self.ds_melee) + int(status_ds_mod or 0))

    def get_bolt_ds(self) -> int:
        """Get bolt defensive strength with status modifiers applied."""
        _status_as_mod, status_ds_mod = get_status_combat_mods(self)
        base = int(getattr(self, "ds_bolt", getattr(self, "ds_ranged", self.ds_melee)) or getattr(self, "ds_ranged", self.ds_melee))
        return max(0, base + int(status_ds_mod or 0))

    def get_udf(self) -> int:
        """Get UDF with status-aware fallback when an explicit value is not set."""
        _status_as_mod, status_ds_mod = get_status_combat_mods(self)
        base = int(getattr(self, "udf", 0) or 0)
        if base <= 0:
            return max(1, self.get_melee_ds())
        return max(1, base + int(status_ds_mod or 0))

    def apply_wound(self, location: str, crit_rank: int) -> int:
        """
        Apply or worsen a wound at the given location based on crit rank.
        Returns new severity (1-5).

        GS4 crit → wound severity:
          rank 1-2 = severity 1 (minor)
          rank 3-4 = severity 2 (moderate)
          rank 5-6 = severity 3 (major)
          rank 7-8 = severity 4 (severe)
          rank 9   = severity 5 (crippling)
        """
        new_sev = min(5, (crit_rank + 1) // 2)
        # Wounds can only worsen, not improve
        current = self.wounds.get(location, 0)
        if new_sev > current:
            self.wounds[location] = new_sev
            if new_sev >= 4:
                if location in {"right hand", "right arm", "left hand", "left arm", "right leg", "left leg"}:
                    self.severed_locations.discard(location)
            if new_sev >= 5:
                self.severed_locations.add(location)
            if location in {"right hand", "right arm"} and new_sev >= 4:
                self.disarmed = True
        return self.wounds.get(location, new_sev)

    def evaluate_combat_impairment(self, location: str, old_sev: int, new_sev: int) -> dict:
        """
        Return combat consequences caused by a worsening wound.
        Used by the combat engine to message drop/sever/stance fallout cleanly.
        """
        result = {
            "dropped_weapon": False,
            "severed": False,
            "location": location,
            "stance_shift": None,
        }
        if new_sev <= old_sev:
            return result
        if location in {"right hand", "right arm"} and new_sev >= 4 and old_sev < 4:
            self.disarmed = True
            result["dropped_weapon"] = True
        if new_sev >= 5 and old_sev < 5:
            result["severed"] = True
            self.severed_locations.add(location)
        if location in {"right leg", "left leg"} and new_sev >= 4:
            result["stance_shift"] = "guarded"
        elif location in {"head", "chest", "abdomen", "right hand", "right arm"} and new_sev >= 4:
            result["stance_shift"] = "defensive"
        return result

    def choose_stance(self):
        """Creature stance AI driven by HP, wounds, and current combat profile."""
        armed = any(self._attack_is_armed(atk) for atk in (self.attacks or []))
        ranged_abilities = {
            "hurl_weapon", "stone_throw", "aimed_shot", "fire_bolt", "water_bolt", "call_wind",
            "acid_spray", "ant_acid_spray", "fire_spit", "tail_spike_volley", "gas_cloud",
            "mind_blast", "sonic_wail", "earthen_fury_caster", "shock_burst",
        }
        ranged_profile = bool(self.spells) or any(
            str(ability or "").lower() in ranged_abilities for ability in (self.abilities or [])
        )
        hp_pct = (self.health_current / self.health_max) if self.health_max else 1.0
        severe_wounds = sum(1 for sev in (self.wounds or {}).values() if int(sev or 0) >= 4)
        leg_disabled = self.location_disabled("right leg") or self.location_disabled("left leg")
        attack_limb_disabled = self.location_disabled("right hand") or self.location_disabled("right arm")

        if leg_disabled or severe_wounds >= 2 or hp_pct <= 0.18:
            self.stance = "defensive"
        elif attack_limb_disabled or hp_pct <= 0.35:
            self.stance = "guarded"
        elif ranged_profile and hp_pct >= 0.45:
            self.stance = "guarded"
        elif armed and hp_pct >= 0.75 and severe_wounds == 0:
            self.stance = "forward"
        elif hp_pct >= 0.90 and not self.wounds:
            self.stance = "advance"
        else:
            self.stance = "neutral"

        preferred = str(getattr(self, "preferred_stance", "") or "").lower().strip()
        profile = str(getattr(self, "stance_profile", "") or "").lower().strip()
        if preferred and hp_pct >= 0.45 and severe_wounds == 0 and not leg_disabled:
            self.stance = preferred
        elif profile == "ranged" and hp_pct >= 0.30 and not leg_disabled:
            self.stance = "guarded"
        elif profile == "berserker" and hp_pct >= 0.25 and severe_wounds == 0:
            self.stance = "forward"
        elif profile == "skirmisher" and hp_pct >= 0.45 and not leg_disabled:
            self.stance = "advance"
        elif profile == "caster" and hp_pct >= 0.35:
            self.stance = "guarded"
        return self.stance

    def wound_summary(self) -> str:
        """Return a short text summary of active wounds for display."""
        if not self.wounds:
            return ""
        SEV_NAMES = {1: "minor", 2: "moderate", 3: "major", 4: "severe", 5: "crippling"}
        parts = [f"{SEV_NAMES.get(sev, 'wounded')} {loc}"
                 for loc, sev in sorted(self.wounds.items(), key=lambda x: -x[1])]
        return ", ".join(parts[:3])  # show worst 3

    def stun(self, duration):
        """Stun the creature for duration seconds."""
        self.stunned_until = time.time() + duration

    def can_act(self):
        """Check if the creature can take an action."""
        self.prune_temporary_effects()
        if self.is_dead:
            return False
        if self.is_stunned:
            return False
        if self.get_roundtime() > 0:
            return False
        active = getattr(self, "status_effects", {}) or {}
        prone_fx = active.get("prone")
        immobile_fx = active.get("immobile")
        if self.prone or (prone_fx and (getattr(prone_fx, "expires", 0) < 0 or time.time() < getattr(prone_fx, "expires", 0))):
            return False
        if self.immobilized or (immobile_fx and (getattr(immobile_fx, "expires", 0) < 0 or time.time() < getattr(immobile_fx, "expires", 0))):
            return False
        return True

    def force_attack_once(self, attack: dict):
        self._forced_attack = dict(attack or {})

    def prune_temporary_effects(self, now=None):
        now = time.time() if now is None else now
        bonuses = getattr(self, "_temp_bonuses", {}) or {}
        stale_bonus = [key for key, row in bonuses.items() if now >= float((row or {}).get("expires", 0) or 0)]
        for key in stale_bonus:
            bonuses.pop(key, None)
        states = getattr(self, "_temp_states", {}) or {}
        stale_states = [key for key, expires in states.items() if now >= float(expires or 0)]
        for key in stale_states:
            states.pop(key, None)

    def apply_temporary_bonus(self, bonus_id: str, duration: float, *, as_bonus=0, ds_bonus=0):
        if not hasattr(self, "_temp_bonuses") or self._temp_bonuses is None:
            self._temp_bonuses = {}
        self._temp_bonuses[str(bonus_id or "").lower()] = {
            "as_bonus": int(as_bonus or 0),
            "ds_bonus": int(ds_bonus or 0),
            "expires": time.time() + max(0.0, float(duration or 0.0)),
        }

    def get_temp_as_bonus(self, now=None):
        self.prune_temporary_effects(now)
        return sum(int((row or {}).get("as_bonus", 0) or 0) for row in (self._temp_bonuses or {}).values())

    def get_temp_ds_bonus(self, now=None):
        self.prune_temporary_effects(now)
        return sum(int((row or {}).get("ds_bonus", 0) or 0) for row in (self._temp_bonuses or {}).values())

    def apply_temporary_state(self, state_id: str, duration: float):
        if not hasattr(self, "_temp_states") or self._temp_states is None:
            self._temp_states = {}
        self._temp_states[str(state_id or "").lower()] = time.time() + max(0.0, float(duration or 0.0))

    def has_temporary_state(self, state_id: str, now=None):
        self.prune_temporary_effects(now)
        states = getattr(self, "_temp_states", {}) or {}
        return str(state_id or "").lower() in states

    def can_cast_spell(self, now=None):
        now = time.time() if now is None else now
        return bool(self.spells) and now >= float(getattr(self, "_last_spell_time", 0.0) or 0.0)

    def set_spell_cooldown(self, seconds):
        self._last_spell_time = time.time() + max(0.0, float(seconds or 0.0))

    def can_use_ability(self, ability_id: str, now=None):
        now = time.time() if now is None else now
        cooldowns = getattr(self, "_ability_cooldowns", {}) or {}
        return now >= float(cooldowns.get(str(ability_id or "").lower(), 0.0) or 0.0)

    def set_ability_cooldown(self, ability_id: str, seconds):
        if not hasattr(self, "_ability_cooldowns") or self._ability_cooldowns is None:
            self._ability_cooldowns = {}
        self._ability_cooldowns[str(ability_id or "").lower()] = time.time() + max(0.0, float(seconds or 0.0))

    def __repr__(self):
        status = "alive" if self.alive else "dead"
        return "Creature(" + str(self.id) + ", " + self.name + ", L" + str(self.level) + ", " + status + ", HP:" + str(self.health_current) + "/" + str(self.health_max) + ")"
