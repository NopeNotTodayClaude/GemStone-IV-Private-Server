-- Creature: spotted gnarp
-- Zone: Victory Road / Rambling Meadows  |  Level: 1
local Creature = {}

Creature.id              = 9103
Creature.name            = "spotted gnarp"
Creature.level           = 1
Creature.family          = "gnarp"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 30
Creature.hp_variance     = 4

Creature.ds_melee        = 20
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type="claw", as=22, damage_type="slash" },
    { type="bite", as=18, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a gnarp hide"
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
    5956,
    5957,
    5958,
    6010
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
    5959,
    5960,
    5961
    }

Creature.roam_chance     = 30
Creature.respawn_seconds = 150
Creature.max_count       = 1

Creature.description = "Barely knee-high, the spotted gnarp has the hunched stance and oversized head of its kind.  Its mottled hide — ivory splotched with irregular dark patches — provides decent camouflage in tall grass.  It skitters on two legs with an unsettling sideways tilt, snapping with needle-sharp teeth at anything within reach."

return Creature
