-- Creature: kobold shepherd
-- Zone: wehnimers_landing / Kobold Mines (zone 15)  |  Level: 3
-- Source: https://gswiki.play.net/Kobold_shepherd
-- HP: 51 | AS: 50 (quarterstaff) | Bolt: Minor Shock/Water 30 AS | CS: Mana Disruption 702 CS 35
-- DS: 57 melee | bolt DS: 54 | UDF: 57 | ASG: 2 (robes) | TD: 9
-- Treasure: coins yes, gems yes, boxes yes | Skin: a kobold shepherd crook
local Creature = {}

Creature.id              = 9333
Creature.name            = "kobold shepherd"
Creature.level           = 3
Creature.family          = "kobold"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 51
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: quarterstaff 50 AS, bolt spells 30 AS (Minor Shock 901, Minor Water 903)
-- CS 35 (Mana Disruption 702 warding), DS 57 melee, bolt DS 54, UDF 57, ASG 2 robes
-- TD not fully listed - using 9 for level 3 standard
Creature.ds_melee        = 57
Creature.ds_bolt         = 54
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 57
Creature.armor_asg       = 2
Creature.armor_natural   = false

Creature.attacks = {
    { type = "staff", as = 50, damage_type = "crush" },
}

Creature.spells = {
    { name = "Minor Shock (901)",       cs = 0,  as = 30, bolt = true },
    { name = "Minor Water (903)",       cs = 0,  as = 30, bolt = true },
    { name = "Mana Disruption (702)",   cs = 35, as = 0  },
}

Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a kobold shepherd crook"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Kobold Mines — sits above the big ugly kobold in the mine hierarchy.
-- Primarily in the deeper sublevel rooms. Hard cap to mine rooms.
Creature.spawn_rooms = {
    8004, 8005, 8006, 8007, 8008,
    8009, 8010, 8011, 8012, 8013,
    8014, 8015, 8016, 8017, 8018,
    8019, 8020, 8021,
}

Creature.roam_rooms = {
    7999, 8000, 8001, 8002, 8003,
    8004, 8005, 8006, 8007, 8008,
    8009, 8010, 8011, 8012, 8013,
    8014, 8015, 8016, 8017, 8018,
    8019, 8020, 8021,
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The kobold shepherd is distinguished from its kin by the long, gnarled quarterstaff it carries and the tattered robes it wears — both signs of status in the mine's hierarchy.  It herds the lesser kobolds with the staff in one hand and casually lobbing bolts of electrical energy with the other.  This casual mastery of two very different forms of violence is, in its way, impressive."

return Creature
