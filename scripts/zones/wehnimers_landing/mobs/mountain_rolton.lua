-- Creature: mountain rolton
-- Zone: wehnimers_landing / Old Mine Road (Upper Trollfang Mine Road area)  |  Level: 1
-- Source: https://gswiki.play.net/Mountain_rolton
-- HP: 28 | AS: 36 (bite) | DS: 28 | bolt: 5 | ASG: 1N natural | TD: 3
-- Treasure: no coins, no gems, no boxes | Skin: a rolton eye
-- Rooms: Mine Road (4196) and adjacent Upper Trollfang rooms in zone 15
local Creature = {}

Creature.id              = 9331
Creature.name            = "mountain rolton"
Creature.level           = 1
Creature.family          = "caprine"
Creature.classification  = "living"
Creature.body_type       = "quadruped"

Creature.hp_base         = 28
Creature.hp_variance     = 4

-- ── Combat ────────────────────────────────────────────────────────────────
-- Wiki: bite 36 AS, DS 28, bolt 5, ASG 1N, TD ~3
Creature.ds_melee        = 28
Creature.ds_bolt         = 5
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 1
Creature.armor_natural   = true

Creature.attacks = {
    { type = "bite",   as = 36, damage_type = "puncture" },
    { type = "charge", as = 36, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = false
Creature.loot_gems    = false
Creature.loot_magic   = false
Creature.loot_boxes   = false
Creature.skin         = "a rolton eye"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Mine Road area in Upper Trollfang (zone 15 / wehnimers_landing).
-- Room 4196 is the Mine Road; surrounding rooms 4106-4117 are adjacent
-- Upper Trollfang terrain where these roltons graze. Hard cap here —
-- they do NOT roam into the goblin/troll zones.
Creature.spawn_rooms = {
    4106, 4107, 4108, 4109,
    4110, 4111, 4112, 4113,
    4114, 4115, 4116, 4117,
    4196, 4197, 4198, 4199,
    4200, 4201, 4202, 4203,
}

Creature.roam_rooms = {
    4106, 4107, 4108, 4109,
    4110, 4111, 4112, 4113,
    4114, 4115, 4116, 4117,
    4196, 4197, 4198, 4199,
    4200, 4201, 4202, 4203,
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 120
Creature.max_count       = 10

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "This is obviously a prime example of the beast of legend, the fiend of song and tale.  Known near and far as an implacable enemy of early settlers, it was this ferocious sheeplike creature that earned the epithet of Warrior-Killer in its sordid past.  The rolton is covered with a dirty, matted, disgusting-looking grey pelt that might once have been white and is still abysmally smelly.  However, it isn't this trait alone that gives him such a terrifying appearance.  As the animal bleats at you, it is then you get a view of the maw of death, with its long, curved incisors that gnash and gnaw."

return Creature
