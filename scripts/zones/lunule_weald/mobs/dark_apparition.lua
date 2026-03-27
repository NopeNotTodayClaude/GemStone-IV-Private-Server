-- Creature: dark apparition
-- Zone: Lunule Weald / Zealot Village  |  Level: 23
local Creature = {}
Creature.id              = 9510
Creature.name            = "dark apparition"
Creature.level           = 23
Creature.family          = "apparition"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 262
Creature.hp_variance     = 18
Creature.ds_melee        = 195
Creature.ds_bolt         = 92
Creature.td_spiritual    = 74
Creature.td_elemental    = 52
Creature.udf             = 278
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="shadow_touch", as=242, damage_type="unbalancing" },
    { type="chill_touch", as=235, damage_type="cold" },
    { type="shadow_bolt", as=228, damage_type="cold" },
}
Creature.spells = {
    { name="shadow_shroud", cs=130, as=0 },
    { name="dark_vision", cs=125, as=0 },
}
Creature.abilities = {
    "spirit_strike",
    "shadow_meld",
    "phase_through_terrain",
    "fear_aura",
    "life_leech",
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
Creature.skin        = ""
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "collapses into a pool of shadow that seeps into the ground."
Creature.spawn_rooms = {
    10597,
    10598,
    10599,
    10600,
    10601,
    10602,
    10603,
    10604,
    10605,
    10606,
    10607,
    10608
    }
Creature.roam_rooms = {
    10597,
    10598,
    10599,
    10600,
    10601,
    10602,
    10603,
    10604,
    10605,
    10606,
    10607,
    10608,
    10594,
    10595,
    10610
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 540
Creature.max_count       = 1
Creature.description = "The dark apparition is shadow with intent — a roughly human-shaped mass of absolute darkness that moves through the ruined Zealot Village as though it owns the place, which in all practical terms it does.  No light penetrates its form; even adjacent torches seem to flicker and dim in its presence.  The cold it radiates is bone-deep and carries the specific quality of despair rather than mere temperature."
return Creature
