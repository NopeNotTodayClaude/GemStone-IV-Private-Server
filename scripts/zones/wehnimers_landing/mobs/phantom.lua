-- Creature: phantom
-- Zone: wehnimers_landing / The Graveyard  |  Level: 2
-- Source: https://gswiki.play.net/Phantom
-- HP: 42 | AS: 28 (closed fist) | Bolt: Minor Shock 35 AS
-- DS: -23 melee / -24 bolt | UDF: 26 | TD: 6 all schools | ASG: 5 (light leather)
-- Classification: non-corporeal undead
-- Treasure: coins yes, gems yes, magic yes, boxes yes | No skin
local Creature = {}

Creature.id              = 9320
Creature.name            = "phantom"
Creature.level           = 2
Creature.family          = "ghost"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"

Creature.hp_base         = 42
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: closed fist 28 AS, dagger 0 AS, Minor Shock (901) bolt 35 AS
-- DS -23 melee, -24 bolt, UDF 26, TD 6 all schools, ASG 5
Creature.ds_melee        = -23
Creature.ds_bolt         = -24
Creature.td_spiritual    = 6
Creature.td_elemental    = 6
Creature.udf             = 26
Creature.armor_asg       = 5
Creature.armor_natural   = false

Creature.attacks = {
    { type = "closed_fist", as = 28, damage_type = "crush" },
}

Creature.spells = {
    { name = "Minor Shock (901)", cs = 0, as = 35, bolt = true },
}

Creature.abilities = {}

Creature.immune = {
    "disease",
    "poison",
}

Creature.resist = {
    "pierce",
    "slash",
    "crush",
}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: coins yes, gems yes, magic yes, boxes yes. No skin.
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = ""
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 60
Creature.crumbles      = true
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- The Graveyard (Wehnimer's Environs) — same rooms as lesser_shade.
-- Roam boundary is hard-capped to the graveyard; phantoms do not
-- drift into the upper trollfang or other zones.
Creature.spawn_rooms = {
    7163, 7164, 7165, 7166, 7167,
    7168, 7169, 7170, 7171, 7172,
    7173, 7174, 7175, 7176, 7177,
    7178, 7179, 7180, 7181, 7182,
    7183, 7184, 7185, 7186, 7187,
    7188, 7189, 7190, 7191, 7192,
    7193, 7194, 7195, 7196, 7197,
    7198, 7199, 7200, 7201, 7202,
    7203, 7204, 7205, 7206, 7207,
    7208, 7209, 7210, 7211, 7212,
    7213, 7214, 7245, 7246, 7247,
    7248, 7249, 7250, 7251, 7252,
    7253, 7254,
}

Creature.roam_rooms = {
    7163, 7164, 7165, 7166, 7167,
    7168, 7169, 7170, 7171, 7172,
    7173, 7174, 7175, 7176, 7177,
    7178, 7179, 7180, 7181, 7182,
    7183, 7184, 7185, 7186, 7187,
    7188, 7189, 7190, 7191, 7192,
    7193, 7194, 7195, 7196, 7197,
    7198, 7199, 7200, 7201, 7202,
    7203, 7204, 7205, 7206, 7207,
    7208, 7209, 7210, 7211, 7212,
    7213, 7214, 7245, 7246, 7247,
    7248, 7249, 7250, 7251, 7252,
    7253, 7254,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 180
Creature.max_count       = 13

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The phantom drifts several inches above the earth, an indistinct shape of pale light and cold air that occasionally resolves into something almost human before losing cohesion again.  The Minor Shock it channels comes less from any training than from raw spiritual agitation — the dead here do not rest, and they make that known."

return Creature
