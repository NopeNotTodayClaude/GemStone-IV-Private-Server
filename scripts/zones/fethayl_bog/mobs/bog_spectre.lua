-- Creature: bog spectre
-- Zone: Fethayl Bog  |  Level: 47
local Creature = {}

Creature.id              = 9017
Creature.name            = "bog spectre"
Creature.level           = 47
Creature.family          = "spectre"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 530
Creature.hp_variance     = 28

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 295
Creature.ds_bolt         = 155
Creature.td_spiritual    = 158
Creature.td_elemental    = 110
Creature.udf             = 312
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type="spectral_touch", as=455, damage_type="unbalancing" },
    { type="spectral_claw", as=448, damage_type="slash" },
}
Creature.spells = {
    { name="spirit_slayer", cs=238, as=0 },
    { name="nightmare", cs=230, as=0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "spirit_strike",
    "phase_through_terrain",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
    "electricity",
}
Creature.resist    = {
    "fire",
}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "dissolves into a wisp of foul vapor."

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    10134,
    10135,
    10136,
    10137,
    10138,
    10139,
    10140,
    10141,
    10142,
    10143,
    10144,
    10145,
    10146,
    10147,
    10148,
    10149
    }

Creature.roam_rooms = {
    10126,
    10127,
    10128,
    10129,
    10130,
    10131,
    10132,
    10133,
    10134,
    10135,
    10136,
    10137,
    10138,
    10139,
    10140,
    10141,
    10142,
    10143,
    10144,
    10145,
    10146,
    10147,
    10148,
    10149,
    10150,
    10151,
    10152,
    10153,
    10154,
    10155,
    10156,
    10157
    }

Creature.roam_chance     = 20
Creature.respawn_seconds = 660
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "A luminous smear of sickly green light given vague humanoid form, the bog spectre drifts above the waterlogged ground without touching it.  Hollow screaming sockets serve as eyes, and a mouth stretched wide in a silent wail completes a visage that seems designed to inspire despair.  The very air chills several degrees in its presence."

return Creature
