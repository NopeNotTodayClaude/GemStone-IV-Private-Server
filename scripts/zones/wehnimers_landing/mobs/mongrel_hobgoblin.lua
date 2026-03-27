-- Creature: mongrel hobgoblin
-- Zone: wehnimers_landing / Wehnimer's Environs (Upper Trollfang)  |  Level: 5
-- Source: https://gswiki.play.net/Mongrel_hobgoblin
-- HP: 80 | AS: 99 (morning star) | DS: 57 | bolt: 3 | UDF: 113 | TD: 15
-- ASG: 8 (double leather) | Classification: living | Body: biped
-- Treasure: coins yes, gems yes, magic yes, boxes yes | Skin: a mongrel hobgoblin snout
local Creature = {}

Creature.id              = 9330
Creature.name            = "mongrel hobgoblin"
Creature.level           = 5
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 80
Creature.hp_variance     = 7

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: morning star 99 AS, DS 57, bolt DS 3, UDF 113, TD 15 (sorc/elemental)
Creature.ds_melee        = 57
Creature.ds_bolt         = 3
Creature.td_spiritual    = 15
Creature.td_elemental    = 15
Creature.udf             = 113
Creature.armor_asg       = 8
Creature.armor_natural   = false

Creature.attacks = {
    { type = "morning_star", as = 99, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = { "hobgoblin_antics" }
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a mongrel hobgoblin snout"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Upper Trollfang — same entry rooms as the L2-L4 pack. Mongrel hobgoblins
-- are the top of the entry-level band. Roam extends slightly deeper into
-- the trollfang scrub alongside coyote_trollfang, but hard cap prevents
-- reaching the level 6+ lesser orc zone (rooms 1196+).
Creature.spawn_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
    472, 473, 474, 475,
}

Creature.roam_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
    472, 473, 474, 475,
}

Creature.roam_chance     = 25
Creature.respawn_seconds = 240
Creature.max_count       = 5

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "The mongrel hobgoblin is a horribly misshapen beast, with a hideously deformed face.  The large, knotted muscles on her arms betray the creature's strength, which is capable of rending a man's limbs right out of their sockets.  Mottled skin with a greenish-yellow hue is splotched with randomly scattered patches of reddish-brown fur.  The dark beady eyes of the hobgoblin glare menacingly, as if crushing the life from someone would somehow make her life more bearable."

return Creature
