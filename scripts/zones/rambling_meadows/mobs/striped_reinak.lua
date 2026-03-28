-- Creature: striped reinak
-- Zone: Rambling Meadows  |  Level: 3
local Creature = {}

Creature.id              = 9106
Creature.name            = "striped reinak"
Creature.level           = 3
Creature.family          = "reinak"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 52
Creature.hp_variance     = 5

Creature.ds_melee        = 36
Creature.ds_bolt         = 16
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 0
Creature.armor_asg       = 2
Creature.armor_natural   = false

Creature.attacks = {
    { type="claw", as=54, damage_type="slash" },
    { type="bite", as=50, damage_type="puncture" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = false
Creature.loot_boxes  = false
Creature.skin        = "a striped relnak sail"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    5985,
    5986,
    5987,
    5988,
    5989,
    5990,
    5991,
    5992,
    5993,
    5970,
    5971,
    5972,
    5973
    }
Creature.roam_rooms = {
    5985,
    5986,
    5987,
    5988,
    5989,
    5990,
    5991,
    5992,
    5993,
    5976,
    5977,
    5978,
    5971,
    5972,
    5973
    }

Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 1

Creature.description = "Striped in alternating bands of tawny gold and dark brown, the reinak presents an almost decorative appearance at odds with its aggressive temperament.  It stands upright on powerful hind legs, forearms tipped with curved claws, and its wide-set eyes track movement across the field with predatory precision."

return Creature
