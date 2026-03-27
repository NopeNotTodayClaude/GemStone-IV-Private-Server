"""
Creature - A living creature/monster in the game world.
Each creature instance is a single spawned mob with its own HP, position, etc.
Creature templates (stats, attacks) are defined in creature_data.py and loaded
from the database or Lua scripts.
"""

import time
import random
import logging
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
        self.description = template.get("description", "You see nothing unusual.")

        # Combat stats (from template)
        self.health_max = template.get("hp", 28)
        self.health_current = self.health_max
        self.as_melee = template.get("as_melee", 40)
        self.ds_melee = template.get("ds_melee", 20)
        self.ds_ranged = template.get("ds_ranged", 20)
        self.ds_bolt = template.get("ds_bolt", 20)
        self.td = template.get("td", 3)  # Target defense (vs magic)
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
        self.skinned = False

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

        # ── Wound tracking (GS4 wiki: wounds reduce AS/DS per location) ──────
        # wounds = {location: severity}  severity 1-5 (minor→crippling)
        # GS4 crit ranks 1-2=minor(1), 3-4=moderate(2), 5-6=major(3), 7-8=severe(4), 9=crippling(5)
        self.wounds: dict = {}
        self.status_effects: dict = {}

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
        if not self.attacks:
            return None
        return random.choice(self.attacks)

    def get_melee_as(self, attack=None):
        """Get attack strength, degraded by wounds and HP percentage."""
        base = attack.get("as", self.as_melee) if attack else self.as_melee

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

        # ── HP-based degradation (GS4 wiki: creatures fight worse when hurt) ─
        if self.health_max > 0:
            hp_pct = self.health_current / self.health_max
            if hp_pct < 0.75:
                hp_penalty = int((0.75 - hp_pct) / 0.75 * 40)
                penalty += hp_penalty

        return max(0, base - penalty)

    def get_melee_ds(self):
        """Get defensive strength, degraded by wounds and HP percentage."""
        ds = self.ds_melee

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

        # ── HP-based degradation ──────────────────────────────────────────────
        if self.health_max > 0:
            hp_pct = self.health_current / self.health_max
            if hp_pct < 0.75:
                hp_penalty = int((0.75 - hp_pct) / 0.75 * 50)
                penalty += hp_penalty

        return max(0, ds - penalty)

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
        return self.wounds.get(location, new_sev)

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

    def __repr__(self):
        status = "alive" if self.alive else "dead"
        return "Creature(" + str(self.id) + ", " + self.name + ", L" + str(self.level) + ", " + status + ", HP:" + str(self.health_current) + "/" + str(self.health_max) + ")"
