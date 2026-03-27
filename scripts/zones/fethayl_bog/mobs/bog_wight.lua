-- Creature: bog wight
-- Zone: Fethayl Bog  |  Level: 44
local Creature = {}

Creature.id              = 9016
Creature.name            = "bog wight"
Creature.level           = 44
Creature.family          = "wight"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 500
Creature.hp_variance     = 30

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 278
Creature.ds_bolt         = 140
Creature.td_spiritual    = 148
Creature.td_elemental    = 148
Creature.udf             = 285
Creature.armor_asg       = 13
Creature.armor_natural   = false

Creature.attacks = {
    { type="claw", as=428, damage_type="slash" },
    { type="bite", as=418, damage_type="puncture" },
    { type="pound", as=412, damage_type="crush" },
}
Creature.spells = {
    { name="dark_catalyst", cs=220, as=0 },
    { name="wither", cs=215, as=0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "wight_drain",
    "life_drain",
    "disease_touch",
}
Creature.immune    = {
    "disease",
    "poison",
}
Creature.resist    = {
    "cold",
}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a wight finger bone"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
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
    10141
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
    10145
    }

Creature.roam_chance     = 15
Creature.respawn_seconds = 600
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Waterlogged and ancient, the bog wight moves with an unnatural deliberateness, its bloated flesh tinged blue-grey with centuries of submersion.  Patches of dark peat cling to rotted clothing that might once have been noble.  Its eyes have the milky pallor of death, yet they fix on you with unmistakable predatory focus."

return Creature
