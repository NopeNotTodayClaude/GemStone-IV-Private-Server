-- Creature: ghoul
-- Zone: tavaalor | Catacombs | Level: 6
-- Source: gswiki.play.net/Ghoul
--
-- Ravenous undead haunting the deepest reaches of the catacombs.
-- Former tomb robbers transformed through exposure to necromantic energies.
-- Retain grotesque human movement but driven only by hunger.
--
-- Special ability: cripple_maneuver — the ghoul's paralyzing touch can
-- immobilize a limb (maneuver roll vs target TD, GS4 canonical ghoul attack).
--
-- GS4 Canon Stats (Level 6):
--   HP: ~75      AS (claw): 74    AS (bite): 68
--   DS: 62       Bolt DS: 42      TD: 18
--   ASG: 3 (thick leathery undead hide, reinforced leather equivalent)
--   Experience: ~185 base exp per kill
-- -----------------------------------------------------------------------
local Creature = {}

Creature.id             = 7005
Creature.name           = "ghoul"
Creature.level          = 6
Creature.family         = "ghoul"
Creature.classification = "corporeal_undead"
Creature.body_type      = "biped"

-- Vitals
Creature.hp_base        = 72
Creature.hp_variance    = 10

-- Combat
Creature.ds_melee       = 62
Creature.ds_bolt        = 42
Creature.td_spiritual   = 18
Creature.td_elemental   = 18
Creature.udf            = 0
Creature.armor_asg      = 3
Creature.armor_natural  = true

Creature.attacks = {
    { type = "claw",  as = 74, damage_type = "slash",    weight = 50 },
    { type = "bite",  as = 68, damage_type = "puncture", weight = 35 },
    { type = "rake",  as = 64, damage_type = "slash",    weight = 15 },
}

Creature.spells    = {}
Creature.abilities = { "cripple_maneuver" }
Creature.immune    = { "poison", "disease" }
Creature.resist    = {}

-- Loot
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a ghoul finger"
Creature.special_loot = {}

-- Decay
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = "The ghoul's body slumps to the ground, its unnatural hunger finally ended."

-- Description
Creature.description = "The ghoul moves with a hunched, lurching gait, its too-long arms nearly dragging on the stone floor.  Its skin is mottled grey-green, stretched tight over visible bone in some places and hanging loose in others.  Yellowed, cracked fingernails curve into hooks perfect for rending flesh.  A thick, fetid odor precedes it."

-- Spawn Rooms — deepest sections only, where necromantic energy pools
Creature.spawn_rooms = {
    5930, 5931,
    5934, 5935,
    5937, 5941, 5942, 5944
}

Creature.roam_rooms = {
    5930, 5931, 5934, 5935,
    5937, 5940, 5941, 5942, 5943, 5944
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 320
Creature.max_count       = 4

return Creature
