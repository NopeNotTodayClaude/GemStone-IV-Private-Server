-- Creature: shelfae chieftain
-- Zone: solhaven / Coastal Cliffs upper + marshtown  |  Level: 11
-- Source: https://gswiki.play.net/Shelfae_chieftain
-- HP: 140 | AS: halberd/morning star 130 | DS: 45 | bolt: 25 | TD: 33
-- ASG: 11 (studded leather) | Body: hybrid | Classification: living
-- Special: tail strike, tremors ability
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a chieftain scale
local Creature = {}

Creature.id              = 10439
Creature.name            = "shelfae chieftain"
Creature.level           = 11
Creature.family          = "shelfae"
Creature.classification  = "living"
Creature.body_type       = "hybrid"

Creature.hp_base         = 140
Creature.hp_variance     = 14

Creature.ds_melee        = 45
Creature.ds_bolt         = 25
Creature.td_spiritual    = 33
Creature.td_elemental    = 33
Creature.udf             = 0
Creature.armor_asg       = 11
Creature.armor_natural   = false

Creature.attacks = {
    { type = "halberd",      as = 130, damage_type = "slash" },
    { type = "morning_star", as = 130, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = { "tail_strike", "tremors" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a shelfae crest"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    7726, 7727, 7728, 7729, 7730,
    7731, 7732, 7733, 7734, 7735,
    7736, 7737, 7738, 7739, 7740,
    7741, 7742, 7743, 7744, 7745,
}

Creature.roam_rooms = {
    7726, 7727, 7728, 7729, 7730,
    7731, 7732, 7733, 7734, 7735,
    7736, 7737, 7738, 7739, 7740,
    7741, 7742, 7743, 7744, 7745,
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 4

Creature.description = "The shelfae chieftain stands half again the height of the soldiers it commands, its overlapping chitin plates scarred and recoloured by a long history of violence. It carries both a halberd and a morning star with the casual ease of something that has decided not to choose between them. The thick tail it uses as a third strike sweeps low and without warning, and the tremors it generates when it lands a full-force blow have knocked more than one opponent off their footing entirely."

return Creature
