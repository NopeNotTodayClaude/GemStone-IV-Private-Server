-- Creature: ghost wolf
-- Zone: glaise_cnoc  |  Level: 16
local Creature = {}

Creature.id              = 2005
Creature.name            = "ghost wolf"
Creature.level           = 16
Creature.family          = "canine"
Creature.classification  = "non_corporeal_undead"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "quadruped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 150
Creature.hp_variance     = 10

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 101
Creature.ds_bolt         = 84
Creature.td_spiritual    = 48
Creature.td_elemental    = 48
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite", as = 143, damage_type = "puncture" },
    { type = "claw", as = 143, damage_type = "slash" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "non_corporeal",
    "pack_hunting",
}

Creature.immune = {
    "disease",
    "poison",
    "normal_weapon",
}

Creature.resist = {

}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = false
Creature.loot_gems       = false
Creature.loot_magic      = false
Creature.loot_boxes      = false
Creature.skin            = ""
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
    10729,
    10730,
    10731,
    10732,
    10733,
    10734,
    10735,
    10736,
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
    10729,
    10730,
    10731,
    10732,
    10733,
    10734,
    10735,
    10736,
}

Creature.roam_chance     = 30   -- % chance to move each tick
Creature.respawn_seconds = 360
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "A transparent, flickering, light-grey canine, the ghost wolf is the captured spirit of a wolf pack member.  It prefers to hunt with others of its kind, watching carefully before darting in to bite, then rushing away while another attacks from the rear."

return Creature
