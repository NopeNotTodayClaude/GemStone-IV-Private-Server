-- Creature: ice hound pack leader
-- Zone: Icemule Trace / Icy Ravine  |  Level: 25
local Creature = {}

Creature.id              = 10318
Creature.name            = "ice hound pack leader"
Creature.level           = 25
Creature.family          = "canine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 330
Creature.hp_variance     = 24
Creature.ds_melee        = 220
Creature.ds_bolt         = 108
Creature.td_spiritual    = 82
Creature.td_elemental    = 82
Creature.udf             = 5
Creature.armor_asg       = 7
Creature.armor_natural   = true

Creature.attacks = {
    { type="bite", as=304, damage_type="puncture" },
    { type="claw", as=294, damage_type="slash" },
    { type="freeze_bite", as=288, damage_type="cold" },
}

Creature.spells = {}
Creature.abilities = { "pack_tactics", "pack_hunting", "cold_immunity", "freeze_bite", "howl_of_dread" }
Creature.immune    = { "cold" }
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = "an ice hound pelt"
Creature.special_loot = { "a frost-rimmed alpha fang" }

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    2571, 3550, 3551, 3552, 3553, 3554, 3559, 3617,
    3678, 3679, 3680, 3681, 3682, 4122, 4123, 4124
}
Creature.roam_rooms = {
    2571, 3550, 3551, 3552, 3553, 3554, 3559, 3617,
    3678, 3679, 3680, 3681, 3682, 4122, 4123, 4124
}

Creature.roam_chance     = 22
Creature.respawn_seconds = 480
Creature.max_count       = 1

Creature.description = "Larger than the rest of its pack and carrying a white ridge of frost-hardened fur down its spine, the ice hound pack leader moves with glacial confidence.  Every growl from its throat drives the rest of the pack into tighter formation."

return Creature
