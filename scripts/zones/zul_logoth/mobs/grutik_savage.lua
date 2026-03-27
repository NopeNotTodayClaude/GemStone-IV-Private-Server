-- Creature: Grutik savage
-- Zone: Zul Logoth / Zaerthu Tunnels  |  Level: 27
local Creature = {}
Creature.id              = 10401
Creature.name            = "Grutik savage"
Creature.level           = 27
Creature.family          = "grutik"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 332
Creature.hp_variance     = 27
Creature.ds_melee        = 228
Creature.ds_bolt         = 110
Creature.td_spiritual    = 86
Creature.td_elemental    = 86
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = false
Creature.attacks         = {
    { type="handaxe", as=325, damage_type="slash" },
    { type="claw", as=316, damage_type="slash" },
    { type="bite", as=308, damage_type="puncture" },
}
Creature.spells          = {}
Creature.abilities       = {
    "tunnel_sight",
    "ambush_attack",
    "battle_fury",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a Grutik ear"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    5782,
    5783,
    5784,
    5785,
    5786,
    5787,
    5788,
    5789,
    5790,
    5791,
    5792,
    5793,
    5794,
    5795,
    5796,
    5797,
    5798,
    5799,
    5800,
    5801
    }
Creature.roam_rooms      = {
    5782,
    5783,
    5784,
    5785,
    5786,
    5787,
    5788,
    5789,
    5790,
    5791,
    5792,
    5793,
    5794,
    5795,
    5796,
    5797,
    5798,
    5799,
    5800,
    5801
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 480
Creature.max_count       = 3
Creature.description     = "The Grutik savage is the warrior caste of the subterranean Grutik people — broader across the shoulders than their shamans, with heavier brow ridges and shorter, more powerful limbs suited to close-quarters tunnel fighting.  The skin is the deep grey-brown of cave-dwellers, and the eyes are adapted to near-total darkness in ways that give them a reflective quality in torchlight.  They fight with the confident efficiency of people who have been winning tunnel battles for generations."
return Creature
