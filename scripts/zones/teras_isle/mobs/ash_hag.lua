-- Creature: ash hag
-- Zone: Teras Isle / Volcanic Slope  |  Level: 31
local Creature = {}
Creature.id              = 10207
Creature.name            = "ash hag"
Creature.level           = 31
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 385
Creature.hp_variance     = 32
Creature.ds_melee        = 258
Creature.ds_bolt         = 125
Creature.td_spiritual    = 100
Creature.td_elemental    = 100
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=378, damage_type="slash" },
    { type="ash_spray", as=370, damage_type="fire" },
}
Creature.spells          = {
    { name="ash_blast", cs=158, as=0 },
    { name="lava_shard", cs=152, as=0 },
    { name="volcanic_curse", cs=148, as=0 },
}
Creature.abilities       = {
    "ash_spray",
    "volcanic_curse",
    "hag_curse",
    "fire_immunity",
}
Creature.immune          = {
    "fire",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "an ash hag tooth"
Creature.special_loot    = {
    "a volcanic obsidian chip",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    12575,
    12576,
    12577,
    12578,
    12579,
    12580,
    12581,
    14694,
    14695,
    14696,
    14699,
    14704
    }
Creature.roam_rooms      = {
    12575,
    12576,
    12577,
    12578,
    12579,
    12580,
    12581,
    14694,
    14695,
    14696,
    14699,
    14704
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 540
Creature.max_count       = 1
Creature.description     = "Living in the volcanic vents and geyser fields, the ash hag has the complexion of cooling lava and the personality to match.  Her hair is white ash perpetually disturbed by heat convection, and the clouds of superheated particles she can project make approaching her directly a poor tactical choice.  The magic she uses draws on the volcanic energy of the island itself, which means she is, in this terrain, essentially never out of power."
return Creature
