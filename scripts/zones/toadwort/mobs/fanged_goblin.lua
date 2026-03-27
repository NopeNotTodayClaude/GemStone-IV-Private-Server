-- Creature: fanged goblin
-- Zone: toadwort  |  Level: 2
local Creature = {}

Creature.id              = 7001
Creature.name            = "fanged goblin"
Creature.level           = 2
Creature.family          = "goblin"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 50
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 55
Creature.ds_bolt         = 0
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 116
Creature.armor_asg       = 7
Creature.armor_natural   = false

Creature.attacks = {
    { type = "handaxe", as = 46, damage_type = "slash" },
    { type = "spear", as = 46, damage_type = "puncture" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "scavenge_weapon",
}

Creature.immune = {

}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a goblin fang"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10499,
    10500,
    10501,
    10502,
    10503,
    10504,
    10505,
    10506,
    10507,
    10508,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10499,
    10500,
    10501,
    10502,
    10503,
    10504,
    10505,
    10506,
    10507,
    10508,
    10509,
    10510,
}

Creature.roam_chance     = 30   -- % chance to move each tick
Creature.respawn_seconds = 240
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Round-headed with a squat nose and wide mouth, the fanged goblin has dark cast green skin with a sickly yellow tinge.  Long, sharp fangs poke out of puffed lips forcing a perpetual sneer.  A yeasty smell of something left to rot completes its aura."

return Creature
