-- Creature: plumed cockatrice
-- Zone: neartofar_forest  |  Level: 13
local Creature = {}

Creature.id              = 6001
Creature.name            = "plumed cockatrice"
Creature.level           = 13
Creature.family          = "basilisk"
Creature.classification  = "living"  -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "hybrid"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 120
Creature.hp_variance     = 10

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 111
Creature.ds_bolt         = 67
Creature.td_spiritual    = 39
Creature.td_elemental    = 39
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "charge", as = 167, damage_type = "crush" },
    { type = "claw", as = 157, damage_type = "slash" },
    { type = "pincer", as = 157, damage_type = "crush" },
}

Creature.spells = {

}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "stare_maneuver",
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
Creature.skin            = "a cockatrice plume"
Creature.special_loot = {

}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false   -- body vanishes on death
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mob will ONLY spawn in these rooms (enforced hard boundary)
Creature.spawn_rooms = {
    10622,
    10623,
    10624,
    10625,
    10626,
    10627,
    10628,
    10629,
    10630,
    10631,
    10632,
    10633,
    10634,
    10635,
    10636,
    10637,
    10638,
    10639,
    10640,
    10641,
    10642,
    10633,
    10636,
    10637,
    10641,
    10642,
}

-- Mob may wander into adjacent rooms within this list only
Creature.roam_rooms = {
    10622,
    10623,
    10624,
    10625,
    10626,
    10627,
    10628,
    10629,
    10630,
    10631,
    10632,
    10633,
    10634,
    10635,
    10636,
    10637,
    10638,
    10639,
    10640,
    10641,
    10642,
    10633,
    10636,
    10637,
    10641,
    10642,
}

Creature.roam_chance     = 25   -- % chance to move each tick
Creature.respawn_seconds = 300
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The plumed cockatrice has a snake-like body, plumes of feathers spearing from its head, dapple grey wings, and short stout legs.  Its cold penetrating gaze is not as deadly as a basilisk's, but its sharp beak and raking claws make it a fierce opponent."

return Creature
