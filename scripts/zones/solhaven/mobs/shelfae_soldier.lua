-- Creature: shelfae soldier  |  Zone: solhaven / Coastal Cliffs (upper) + marshtown  |  Level: 7
-- Source: gswiki.play.net/Shelfae_soldier
-- HP: 100 | AS: trident 102 AS | DS: 41 | bolt: 13 | TD: 21 | ASG: 11
local Creature = {}

Creature.id              = 10429
Creature.name            = "shelfae soldier"
Creature.level           = 7
Creature.family          = "shelfae"
Creature.classification  = "living"
Creature.body_type       = "hybrid"

Creature.hp_base         = 100
Creature.hp_variance     = 10

Creature.ds_melee        = 41
Creature.ds_bolt         = 13
Creature.td_spiritual    = 21
Creature.td_elemental    = 21
Creature.udf             = 0
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
    7726, 7727, 7728, 7729, 7730, 7731, 7732, 7733, 7734, 7735, 7736, 7737, 7738, 7739, 7740
}

Creature.roam_rooms = {
    7726, 7727, 7728, 7729, 7730, 7731, 7732, 7733, 7734, 7735, 7736, 7737, 7738, 7739, 7740
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 5

Creature.description = "The shelfae soldier wades through the shallows with equal confidence as it moves across the rocks, its trident held at the ready in one claw-hand and its shell offering lateral protection against counter-strikes. It fights in formation when there are others nearby and alone when there are not, and neither changes its expression."

return Creature
