-- Creature: warrior shade
-- Zone: Fethayl Bog  |  Level: 48
local Creature = {}

Creature.id              = 9018
Creature.name            = "warrior shade"
Creature.level           = 48
Creature.family          = "shade"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 545
Creature.hp_variance     = 28

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 305
Creature.ds_bolt         = 160
Creature.td_spiritual    = 162
Creature.td_elemental    = 112
Creature.udf             = 325
Creature.armor_asg       = 1
Creature.armor_natural   = false

Creature.attacks = {
    { type="shadow_blade", as=465, damage_type="slash" },
    { type="shadow_strike", as=460, damage_type="unbalancing" },
    { type="shadow_crush", as=452, damage_type="crush" },
}
Creature.spells = {
    { name="shadow_dispel", cs=242, as=0 },
    { name="darkness_burst", cs=238, as=0 },
}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "spirit_strike",
    "shadow_meld",
    "unbalancing_blow",
    "battle_trained",
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
Creature.loot_boxes  = true
Creature.skin        = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "shatters into fragments of shadow and is gone."

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
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

Creature.roam_rooms = {
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

Creature.roam_chance     = 12
Creature.respawn_seconds = 720
Creature.max_count       = 3

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Once a powerful warrior in life, this shade retains the musculature and posture of combat mastery even in undeath.  Darkness pools around it like a living cloak, and the weapons it carries seem forged from shadow itself — edges that cut with cold precision.  It moves as though still following orders from a commander long since dust."

return Creature
