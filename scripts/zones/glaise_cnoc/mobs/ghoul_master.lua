-- Creature: ghoul master
-- Zone: glaise_cnoc  |  Level: 16
local Creature = {}

Creature.id              = 2006
Creature.name            = "ghoul master"
Creature.level           = 16
Creature.family          = "ghoul"
Creature.classification  = "corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 145
Creature.hp_variance     = 10

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 81
Creature.ds_bolt         = 38
Creature.td_spiritual    = 48
Creature.td_elemental    = 48
Creature.udf             = 211
Creature.armor_asg       = 14
Creature.armor_natural   = false

Creature.attacks = {
    { type = "bite", as = 137, damage_type = "puncture" },
    { type = "claw", as = 147, damage_type = "slash" },
    { type = "pound", as = 137, damage_type = "crush" },
}

Creature.spells = {
    { name = "gesture_warding", cs = 88, as = 0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "ghoul_rot_chance",
    "sulfurous_appearance",
    "ghoul_master_aura",
}

Creature.immune = {
    "disease",
    "poison",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a ghoul master claw"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10716,
    10717,
    10718,
    10719,
    10720,
    10721,
    10722,
    10723,
    10724,
    10725,
    10726,
    10727,
    10728,
    10716,
    10717,
    10718,
    10719,
    10720,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10716,
    10717,
    10718,
    10719,
    10720,
    10721,
    10722,
    10723,
    10724,
    10725,
    10726,
    10727,
    10728,
}

Creature.roam_chance     = 10   -- % chance to move each tick
Creature.respawn_seconds = 420
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Broader and taller than the common ghouls, this one stands with cold bearing of command and power.  Tattered rags of velvet and silk drape its corrupt form and keen evil dominates the ruined, festering face.  Its aura tingles along the nerves."

return Creature
