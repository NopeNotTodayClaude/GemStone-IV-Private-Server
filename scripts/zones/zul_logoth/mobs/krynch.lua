-- Creature: krynch
-- Zone: Zul Logoth / Mraent Cavern  |  Level: 31
local Creature = {}
Creature.id              = 10408
Creature.name            = "krynch"
Creature.level           = 31
Creature.family          = "krynch"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 385
Creature.hp_variance     = 32
Creature.ds_melee        = 258
Creature.ds_bolt         = 125
Creature.td_spiritual    = 100
Creature.td_elemental    = 100
Creature.udf             = 8
Creature.armor_asg       = 9
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=378, damage_type="slash" },
    { type="bite", as=370, damage_type="puncture" },
    { type="stone_throw", as=360, damage_type="crush" },
}
Creature.spells          = {}
Creature.abilities       = {
    "tunnel_sight",
    "stone_throw",
    "rock_camouflage",
    "armoured_hide",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a krynch hide plate"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    5776,
    5777,
    5778,
    5779,
    5780,
    5781,
    9459,
    9460,
    9461,
    9462,
    9463,
    9464,
    9465,
    9466,
    9467,
    9468
    }
Creature.roam_rooms      = {
    5776,
    5777,
    5778,
    5779,
    5780,
    5781,
    9459,
    9460,
    9461,
    9462,
    9463,
    9464,
    9465,
    9466,
    9467,
    9468
    }
Creature.roam_chance     = 12
Creature.respawn_seconds = 540
Creature.max_count       = 2
Creature.description     = "The krynch is a large, semi-bipedal creature with overlapping stone-grey hide plates that make it difficult to distinguish from natural rock formations when still.  The face is flat and wide with eyes that have the reflective quality of polished obsidian.  It has learned to use stone as tools and weapons — not forged ones, but selected, thrown, and deployed with surprising accuracy.  In tunnels, this makes it extremely effective."
return Creature
