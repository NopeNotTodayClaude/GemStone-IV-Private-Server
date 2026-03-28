-- Creature: hobgoblin
-- Zone: wehnimers_landing / The Graveyard + Wehnimer's Environs  |  Level: 3
-- Source: https://gswiki.play.net/Hobgoblin
-- HP: 60 | AS: 68 (claidhmore/handaxe/rapier) | DS: 4-25 (mid 15) | UDF: 54-60 | TD: 9
-- ASG: ? (using 7 reinforced leather, consistent with level 3 humanoid)
-- Treasure: coins yes, gems yes, boxes yes | Skin: hobgoblin ear
local Creature = {}

Creature.id              = 9322
Creature.name            = "hobgoblin"
Creature.level           = 3
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 60
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 15
Creature.ds_bolt         = 9
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 57
Creature.armor_asg       = 7
Creature.armor_natural   = false

Creature.attacks = {
    { type = "claidhmore", as = 68, damage_type = "slash" },
    { type = "handaxe",    as = 68, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "scavenge_weapon" }
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a hobgoblin scalp"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Graveyard rooms (7163-7254) + trollfang entry (452-467).
-- Hard boundary — will not reach deeper trollfang or catacombs.
Creature.spawn_rooms = {
    7163, 7164, 7165, 7166, 7167,
    7168, 7169, 7170, 7171, 7172,
    7173, 7174, 7175, 7176, 7177,
    452,  453,  454,  455,
    456,  457,  458,  459,
    460,  461,  462,  463,
}

Creature.roam_rooms = {
    7163, 7164, 7165, 7166, 7167,
    7168, 7169, 7170, 7171, 7172,
    7173, 7174, 7175, 7176, 7177,
    452,  453,  454,  455,
    456,  457,  458,  459,
    460,  461,  462,  463,
    464,  465,  466,  467,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 200
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Larger and meaner than a goblin by an order of magnitude, the hobgoblin compensates for its relative lack of cunning with brute aggression and an oversized weapon it swings with more enthusiasm than skill.  Lumpy grey-green skin and heavy brow ridges give it a permanently furious expression that its behavior tends to justify."

return Creature
