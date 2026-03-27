-- Creature: soul golem
-- Zone: Teras Isle / Temple of Luukos  |  Level: 63
local Creature = {}
Creature.id              = 10213
Creature.name            = "soul golem"
Creature.level           = 63
Creature.family          = "golem"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 742
Creature.hp_variance     = 61
Creature.ds_melee        = 470
Creature.ds_bolt         = 238
Creature.td_spiritual    = 202
Creature.td_elemental    = 202
Creature.udf             = 475
Creature.armor_asg       = 15
Creature.armor_natural   = false
Creature.attacks         = {
    { type="fist", as=728, damage_type="crush" },
    { type="slam", as=718, damage_type="crush" },
    { type="soul_drain", as=708, damage_type="unbalancing" },
}
Creature.spells          = {
    { name="soul_siphon", cs=320, as=0 },
    { name="animate_dead", cs=315, as=0 },
}
Creature.abilities       = {
    "undead_resilience",
    "soul_drain",
    "crushing_grip",
    "immunity_to_stun",
    "golem_slam",
}
Creature.immune          = {
    "disease",
    "poison",
    "cold",
    "electricity",
    "fire",
}
Creature.resist          = {
    "slash",
    "pierce",
}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a golem soul crystal"
Creature.special_loot    = {
    "a cracked soul vessel",
    "a Luukos temple token",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    2159,
    2160,
    2161,
    2162,
    2163,
    2164,
    2165,
    2166,
    2173,
    2174,
    12764,
    12765,
    12766,
    12767
    }
Creature.roam_rooms      = {
    2159,
    2160,
    2161,
    2162,
    2163,
    2164,
    2165,
    2166,
    2173,
    2174,
    12764,
    12765,
    12766,
    12767
    }
Creature.roam_chance     = 5
Creature.respawn_seconds = 1200
Creature.max_count       = 1
Creature.description     = "Constructed by the priests of Luukos from stone and the souls of their sacrificed faithful, the soul golem is a theological statement as much as a weapon.  The stone form is carved with serpent iconography, and the purple-white glow visible through the joins between plates is the trapped souls powering the construct.  It speaks, occasionally, in a chorus of voices — all of them pleading."
return Creature
