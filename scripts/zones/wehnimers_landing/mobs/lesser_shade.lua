-- Creature: lesser shade
-- Zone: WL Graveyard  |  Level: 2
local Creature = {}
Creature.id              = 9307
Creature.name            = "lesser shade"
Creature.level           = 2
Creature.family          = "shade"
Creature.classification  = "non_corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 40
Creature.hp_variance     = 4
Creature.ds_melee        = 38
Creature.ds_bolt         = 18
Creature.td_spiritual    = 10
Creature.td_elemental    = 5
Creature.udf             = 30
Creature.armor_asg       = 1
Creature.armor_natural   = false
Creature.attacks = {
    { type="spectral_touch", as=38, damage_type="unbalancing" },
    { type="chill_touch", as=34, damage_type="cold" },
}
Creature.spells = {}
Creature.abilities = {
    "spirit_strike",
    "chill_touch",
    "fear_aura",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
}
Creature.resist    = {
    "electricity",
}
Creature.loot_coins  = false
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = false
Creature.skin        = ""
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = true
Creature.decay_message = "dissipates into faint wisps of shadow."
Creature.spawn_rooms = {
    7163,
    7164,
    7165,
    7166,
    7167,
    7168,
    7169,
    7170,
    7171,
    7172,
    7173,
    7174,
    7175,
    7176,
    7177,
    7178,
    7179,
    7180,
    7181,
    7182,
    7183,
    7184,
    7185,
    7186,
    7187,
    7188,
    7189,
    7190,
    7191,
    7192,
    7193,
    7194,
    7195,
    7196,
    7197,
    7198,
    7199,
    7200,
    7201,
    7202,
    7203,
    7204,
    7205,
    7206,
    7207,
    7208,
    7209,
    7210,
    7211,
    7212,
    7213,
    7214,
    7245,
    7246,
    7247,
    7248,
    7249,
    7250,
    7251,
    7252,
    7253,
    7254
    }
Creature.roam_rooms = {
    7163,
    7164,
    7165,
    7166,
    7167,
    7168,
    7169,
    7170,
    7171,
    7172,
    7173,
    7174,
    7175,
    7176,
    7177,
    7178,
    7179,
    7180,
    7181,
    7182,
    7183,
    7184,
    7185,
    7186,
    7187,
    7188,
    7189,
    7190,
    7191,
    7192,
    7193,
    7194,
    7195,
    7196,
    7197,
    7198,
    7199,
    7200,
    7201,
    7202,
    7203,
    7204,
    7205,
    7206,
    7207,
    7208,
    7209,
    7210,
    7211,
    7212,
    7213,
    7214,
    7245,
    7246,
    7247,
    7248,
    7249,
    7250,
    7251,
    7252,
    7253,
    7254
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 9
Creature.description = "A vague humanoid outline of condensed shadow, the lesser shade drifts among the gravestones with the purposeless, terrible patience of the unquiet dead.  It has no features — no face, no hands, no distinguishing characteristics — just a darkness that is somehow more present and dense than the surrounding night.  Cold radiates from it in waves."
return Creature
