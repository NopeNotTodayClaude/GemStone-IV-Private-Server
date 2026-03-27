-- Creature: swamp hag
-- Zone: Oteska's Haven  |  Level: 42
local Creature = {}
Creature.id              = 10012
Creature.name            = "swamp hag"
Creature.level           = 42
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 518
Creature.hp_variance     = 43
Creature.ds_melee        = 335
Creature.ds_bolt         = 168
Creature.td_spiritual    = 136
Creature.td_elemental    = 136
Creature.udf             = 0
Creature.armor_asg       = 6
Creature.armor_natural   = false
Creature.attacks         = {
    { type="claw", as=405, damage_type="slash" },
    { type="bite", as=398, damage_type="puncture" },
}
Creature.spells          = {
    { name="poison_mist", cs=215, as=0 },
    { name="bog_curse", cs=210, as=0 },
    { name="disease_cloud", cs=205, as=0 },
}
Creature.abilities       = {
    "hag_curse",
    "poison_touch",
    "disease_cloud",
    "bog_mire_trap",
}
Creature.immune          = {
    "poison",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a swamp hag tooth"
Creature.special_loot    = {
    "a foul-smelling witch's brew",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147
    }
Creature.roam_rooms      = {
    11667,
    11668,
    11669,
    11671,
    11672,
    11673,
    11674,
    11677,
    11678,
    16147,
    11661,
    11662,
    11663
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 600
Creature.max_count       = 1
Creature.description     = "The swamp hag is the apex predator of Oteska's Haven — not through physical power, though she has that, but through cunning accumulated over a lifetime spent in the deepest swamp.  Her skin has taken on the mottled green-grey of the water she inhabits, and the hair that hangs in ropes around her face is indistinguishable from swamp weed.  The laugh she produces when a plan comes together is perhaps the most disturbing sound the Haven produces."
return Creature
