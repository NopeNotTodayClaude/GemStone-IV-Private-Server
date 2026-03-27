-- Creature: Tomb Troll Necromancer
-- Zone: Marsh Keep  |  Level: 54
local Creature = {}
Creature.id              = 10019
Creature.name            = "Tomb Troll Necromancer"
Creature.level           = 54
Creature.family          = "troll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 645
Creature.hp_variance     = 53
Creature.ds_melee        = 408
Creature.ds_bolt         = 205
Creature.td_spiritual    = 175
Creature.td_elemental    = 175
Creature.udf             = 0
Creature.armor_asg       = 12
Creature.armor_natural   = true
Creature.attacks         = {
    { type="claw", as=512, damage_type="slash" },
    { type="staff", as=502, damage_type="crush" },
}
Creature.spells          = {
    { name="animate_dead", cs=275, as=0 },
    { name="necrotic_bolt", cs=270, as=0 },
    { name="wither", cs=265, as=0 },
    { name="disease_cloud", cs=260, as=0 },
}
Creature.abilities       = {
    "troll_regeneration",
    "summon_undead",
    "necromantic_mastery",
    "aura_of_undeath",
}
Creature.immune          = {
    "disease",
    "poison",
}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a tomb troll necromancer's robe scrap"
Creature.special_loot    = {
    "a necromantic tome fragment",
    "a bone scroll case",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    11738,
    11739,
    11740,
    11741,
    11742,
    11743,
    11744,
    11745,
    11746,
    16179,
    16181,
    16209,
    16210,
    16213,
    17692
    }
Creature.roam_rooms      = {
    11738,
    11739,
    11740,
    11741,
    11742,
    11743,
    11744,
    11745,
    11746,
    16179,
    16181,
    16209,
    16210,
    16213,
    17692
    }
Creature.roam_chance     = 5
Creature.respawn_seconds = 900
Creature.max_count       = 1
Creature.description     = "A Tomb Troll that has, over many years in the keep's library, taught itself the rudiments of necromancy — and then considerably more than the rudiments.  It wears the tattered remnants of a scholar's robe over its natural hide, and the staff it carries is wound with bones.  The combination of troll physical resilience with genuine necromantic capability makes this one of the more dangerous inhabitants of the keep.  Fortunately its intellectual development has not extended to tactical awareness."
return Creature
