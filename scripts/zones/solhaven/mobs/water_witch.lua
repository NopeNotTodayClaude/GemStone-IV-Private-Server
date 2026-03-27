-- Creature: water witch
-- Zone: Vornavis / Lower Dragonsclaw  |  Level: 5
local Creature = {}
Creature.id              = 10114
Creature.name            = "water witch"
Creature.level           = 5
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 72
Creature.hp_variance     = 6
Creature.ds_melee        = 55
Creature.ds_bolt         = 28
Creature.td_spiritual    = 16
Creature.td_elemental    = 16
Creature.udf             = 0
Creature.armor_asg       = 4
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=75, damage_type="slash" },
    { type="staff", as=70, damage_type="crush" },
}
Creature.spells          = {
    { name="water_bolt", cs=35, as=0 },
    { name="entangle", cs=30, as=0 },
}
Creature.abilities       = {
    "water_bolt",
    "bog_mire",
    "cackle_fear",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a witch's fingernail"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    213,
    214,
    215,
    216,
    217,
    218,
    219,
    421,
    422,
    423,
    424,
    425
    }
Creature.roam_rooms      = {
    213,
    214,
    215,
    216,
    217,
    218,
    219,
    421,
    422,
    423,
    424,
    425
    }
Creature.roam_chance     = 22
Creature.respawn_seconds = 200
Creature.max_count       = 1
Creature.description     = "The water witch has the withered, brine-pickled look of something that has lived near salt water for decades longer than any human lifespan should allow.  The cloak of kelp and sea-grass she wears drips continuously, and the hair beneath it has the grey-green colour of deep water.  The magic she works is tied to water in all its forms — including the considerable amount currently in the air of the Lower Dragonsclaw."
return Creature
