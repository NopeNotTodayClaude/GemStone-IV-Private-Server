-- Creature: shelfae guard  |  Zone: cliffwalk / Cliffwalk  |  Level: 7
-- Source: GUESSED - wiki blank, balanced vs shelfae soldier L7 (trident 102 AS)
-- HP: 95 | AS: spear 110 AS (guessed) | DS: 55 | bolt: 30 | TD: 21 | ASG: 11
local Creature = {}

Creature.id              = 10428
Creature.name            = "shelfae guard"
Creature.level           = 7
Creature.family          = "shelfae"
Creature.classification  = "living"
Creature.body_type       = "hybrid"

Creature.hp_base         = 95
Creature.hp_variance     = 9

Creature.ds_melee        = 55
Creature.ds_bolt         = 30
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 85
Creature.armor_asg       = 11
Creature.armor_natural   = false

Creature.attacks = {

}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a shelfae scale"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    29120, 29124, 29128, 29129, 29131, 29133, 29134, 29217, 29218, 29219, 29220, 29221, 29222
}

Creature.roam_rooms = {
    29120, 29124, 29128, 29129, 29131, 29133, 29134, 29217, 29218, 29219, 29220, 29221, 29222
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 5

Creature.description = "The shelfae guard is a half-shell creature built on a humanoid frame, its carapace covering the torso and shoulders in overlapping plates of mottled grey-green chitin. It stands patrol with the rigid attention of something trained rather than instinctual, spear carried at a formal angle, eyes tracking movement on the clifface with the patience of a creature that has nowhere better to be."

return Creature
