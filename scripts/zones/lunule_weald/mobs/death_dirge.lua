-- Creature: death dirge
-- Zone: Lunule Weald / Perish Glen  |  Level: 18
local Creature = {}
Creature.id              = 9507
Creature.name            = "death dirge"
Creature.level           = 18
Creature.family          = "spirit"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 210
Creature.hp_variance     = 15
Creature.ds_melee        = 155
Creature.ds_bolt         = 74
Creature.td_spiritual    = 58
Creature.td_elemental    = 40
Creature.udf             = 222
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="wail", as=199, damage_type="unbalancing" },
    { type="spectral_touch", as=194, damage_type="cold" },
}
Creature.spells = {
    { name="sonic_wail", cs=105, as=0 },
}
Creature.abilities = {
    "spirit_strike",
    "sonic_wail",
    "stunning_keen",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
}
Creature.resist    = {}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = "a dirge skin"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "fades with a sound like a last breath."
Creature.spawn_rooms = {
    10578,
    10579,
    10580,
    10581,
    10582,
    10583,
    10584,
    10585,
    10586,
    10587
    }
Creature.roam_rooms = {
    10578,
    10579,
    10580,
    10581,
    10582,
    10583,
    10584,
    10585,
    10586,
    10587,
    10574,
    10575,
    10576,
    10577
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 420
Creature.max_count       = 1
Creature.description = "The death dirge has no visible form — it is pure sound given malevolent existence, a sustained keening at the edge of hearing that builds into something physically painful at close range.  Where it passes, the air resonates with undertones that vibrate in the bones and the teeth.  It manifests visually only as a slight distortion of the air, a shimmer like heat haze in the darkness of Perish Glen."
return Creature
