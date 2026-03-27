-- Creature: Gnoil thief
-- Zone: Upper Trollfang / Mountain Pass  |  Level: 13
local Creature = {}
Creature.id              = 9409
Creature.name            = "Gnoil thief"
Creature.level           = 13
Creature.family          = "gnoll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 168
Creature.hp_variance     = 12
Creature.ds_melee        = 120
Creature.ds_bolt         = 58
Creature.td_spiritual    = 43
Creature.td_elemental    = 43
Creature.udf             = 8
Creature.armor_asg       = 6
Creature.armor_natural   = false
Creature.attacks = {
    { type="dagger", as=165, damage_type="puncture" },
    { type="short_sword", as=160, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {
    "hide_in_shadows",
    "backstab",
    "stealth_ambush",
    "pickpocket_attempt",
}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a gnoll hide"
Creature.special_loot = {
    "a stolen coin purse",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    4197,
    4198,
    4199,
    4200,
    4201,
    4202,
    4203,
    4204
    }
Creature.roam_rooms = {
    4197,
    4198,
    4199,
    4200,
    4201,
    4202,
    4203,
    4204,
    4205,
    4206,
    4207,
    4208,
    4209,
    1289,
    1290,
    1291,
    1292
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 320
Creature.max_count       = 1
Creature.description = "Leaner than its warrior kin and dressed in muted browns and greys that blend into the mountain pass terrain, the Gnoil thief relies on ambush and stealth rather than brute force.  Its spotted hyena-like face wears a permanent expression of scheming cunning, and fingers adapted for quick, light work are never far from whoever it is sizing up."
return Creature
