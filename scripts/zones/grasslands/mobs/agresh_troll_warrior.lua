-- Creature: Agresh troll warrior
-- Zone: Grasslands / Vineyard  |  Level: 16
local Creature = {}

Creature.id              = 9005
Creature.name            = "Agresh troll warrior"
Creature.level           = 16
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 202
Creature.hp_variance     = 16

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 133
Creature.ds_bolt         = 65
Creature.td_spiritual    = 51
Creature.td_elemental    = 51
Creature.udf             = 0
Creature.armor_asg       = 10
Creature.armor_natural   = false

Creature.attacks = {
    { type = "morning_star", as = 190, damage_type = "crush" },
    { type = "handaxe", as = 185, damage_type = "slash" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
Creature.abilities = {
    "troll_regeneration",
    "battle_fury",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a troll scalp"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
Creature.spawn_rooms = {
    10240,
    10241,
    10242,
    10243,
    10244,
    10245,
    10246,
    10247,
    10248,
    10249,
    10250,
    10251,
    10252,
    10262,
    10263,
    10264,
    10265,
    10266,
    10267
}

Creature.roam_rooms = {
    10240,
    10241,
    10242,
    10243,
    10244,
    10245,
    10246,
    10247,
    10248,
    10249,
    10250,
    10251,
    10252,
    10262,
    10263,
    10264,
    10265,
    10266,
    10267,
    10208,
    10209,
    10210,
    10211
}

Creature.roam_chance     = 18
Creature.respawn_seconds = 360
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Armored in pieced-together scale and scarred hide, the Agresh troll warrior is built for nothing but combat.  A thick neck supports a broad, heavy-browed head, and its arms are corded with muscle from years of swinging crude but effective weapons.  It regards you with dim but hostile intelligence."

return Creature
