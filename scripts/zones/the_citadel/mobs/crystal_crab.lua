-- crystal crab L8 | the_citadel / River Tunnels (Thurfel's Keep area) | ID 10430
local Creature = {}

Creature.id              = 10430
Creature.name            = "crystal crab"
Creature.level           = 8
Creature.family          = "crab"
Creature.classification  = "living"
Creature.body_type       = "crustacean"

Creature.hp_base         = 85
Creature.hp_variance     = 8

Creature.ds_melee        = 51
Creature.ds_bolt         = 44
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 70
Creature.armor_asg       = 9
Creature.armor_natural   = true

Creature.attacks = {
    { type = "ensnare", as = 122, damage_type = "crush" },
}

Creature.spells = {

}
Creature.abilities = {  }
Creature.immune    = {  }
Creature.resist    = {}

Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a crystal crab claw"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    11181, 11182, 11183, 11184, 11185, 11186, 11187, 11188, 11189, 11190, 11191, 11192, 11193, 11194, 11195
}

Creature.roam_rooms = {
    11181, 11182, 11183, 11184, 11185, 11186, 11187, 11188, 11189, 11190, 11191, 11192, 11193, 11194, 11195
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 260
Creature.max_count       = 5

Creature.description = "The crystal crab's shell has the translucent quality of thick glass, refracting the limited light of the tunnels in cold prismatic flashes. Its claws are disproportionately large and the ensnare they deliver is essentially mechanical — a grip that closes and does not release. Fighting one is less a question of defeating it than of persuading its nervous system to stop."

return Creature
