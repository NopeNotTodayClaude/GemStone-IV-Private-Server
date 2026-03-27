-- Creature: black rolton
-- Zone: Victory Road / Rambling Meadows  |  Level: 1
local Creature = {}

Creature.id              = 9102
Creature.name            = "black rolton"
Creature.level           = 1
Creature.family          = "rolton"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 32
Creature.hp_variance     = 4

Creature.ds_melee        = 22
Creature.ds_bolt         = 5
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type="headbutt", as=20, damage_type="crush" },
    { type="bite", as=16, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = false
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a rolton fleece"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5950,
    5951,
    5952,
    5953,
    5954,
    5955,
    5974,
    5994
    }
Creature.roam_rooms = {
    5950,
    5951,
    5952,
    5953,
    5954,
    5955,
    5956,
    5957,
    5958,
    6010,
    5974,
    5994
    }

Creature.roam_chance     = 35
Creature.respawn_seconds = 150
Creature.max_count       = 1

Creature.description = "A stocky, short-legged sheep with a coat of shaggy black wool, the black rolton seems perpetually irritated.  Amber eyes with rectangular pupils regard you with the bold hostility that makes these creatures unexpectedly troublesome.  The curved horns on the male look capable of leaving a real impression."

return Creature
