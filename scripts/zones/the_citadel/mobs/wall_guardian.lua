-- Creature: wall guardian
-- Zone: the_citadel / Thurfel's Keep (River Tunnels deep)  |  Level: 11
-- Source: https://gswiki.play.net/Wall_guardian
-- HP: 140 | AS: military pick 100-153 (mid 127) | DS: 53 | bolt: 45 | UDF: 109 | TD: 33
-- ASG: 16 (chain hauberk) | Body: biped | Classification: living
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a guardian finger
local Creature = {}

Creature.id              = 10440
Creature.name            = "wall guardian"
Creature.level           = 11
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 140
Creature.hp_variance     = 14

Creature.ds_melee        = 53
Creature.ds_bolt         = 45
Creature.td_spiritual    = 33
Creature.td_elemental    = 33
Creature.udf             = 109
Creature.armor_asg       = 16
Creature.armor_natural   = false

Creature.attacks = {
    { type = "military_pick", as = 127, damage_type = "puncture" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a guardian finger"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11241, 11242, 11243, 11244, 11245,
    11246, 11247, 11248, 11249, 11250,
    11251, 11252, 11253, 11254, 11255,
    11256, 11257, 11258, 11259, 11260,
}

Creature.roam_rooms = {
    11241, 11242, 11243, 11244, 11245,
    11246, 11247, 11248, 11249, 11250,
    11251, 11252, 11253, 11254, 11255,
    11256, 11257, 11258, 11259, 11260,
}

Creature.roam_chance     = 10
Creature.respawn_seconds = 300
Creature.max_count       = 5

Creature.description = "The wall guardian is enormously broad and wears chain hauberk as though it were a second skin — which, given how long it has been here, is nearly accurate. It carries a military pick with both hands and holds a fixed post with the conviction of something that has been stationed at this section of tunnel since before anyone currently alive was born. It does not pursue. It does not warn. It simply strikes anything that passes through its section without authorisation."

return Creature
