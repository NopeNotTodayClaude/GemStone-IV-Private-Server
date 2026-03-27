-- Creature: kobold
-- Zone: fearling_pass / Briar Thicket  |  Level: 1
-- Source: https://gswiki.play.net/Kobold  (Briar Thicket area, level 1)
-- NOTE: The tavaalor/mobs/kobold.lua (ID 7010) handles the cobbled road and
--       rocky trail rooms (3557, 6101, 10121-10165) at level 2.
--       This file covers the Briar Thicket proper (10166-10170, 10270).
local Creature = {}

Creature.id              = 9009
Creature.name            = "kobold"
Creature.level           = 1
Creature.family          = "kobold"
Creature.classification  = "living"       -- living / corporeal_undead / non_corporeal_undead
Creature.body_type       = "biped"        -- biped / quadruped / ophidian / hybrid

Creature.hp_base         = 40
Creature.hp_variance     = 5

-- ── Combat ────────────────────────────────────────────────────────────────
-- Stats from gswiki.play.net/Kobold: DS melee 18, TD 3, short sword AS 36
Creature.ds_melee        = 18
Creature.ds_bolt         = 8
Creature.td_spiritual    = 3
Creature.td_elemental    = 3
Creature.udf             = 0
Creature.armor_asg       = 5              -- soft leather equivalent
Creature.armor_natural   = false

Creature.attacks = {
    { type = "short_sword", as = 36, damage_type = "slash" },
}

Creature.spells = {}

-- ── Special Abilities ─────────────────────────────────────────────────────
-- Kobolds work in pairs; knock-down chance when 2+ in room
Creature.abilities = {
    "kobold_pair_knockdown",
}

Creature.immune = {}

Creature.resist = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Wiki: coins yes, gems yes, magic yes, boxes yes, skin: kobold skin
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a kobold skin"
Creature.special_loot = {
    "a kobold ear",
}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Briar Thicket rooms only — the briars and brambles outside the Amaranth Gate.
-- Roam boundary is hard-capped to this thicket; they do NOT spill into
-- the higher-level pass rooms to the north.
Creature.spawn_rooms = {
    10166,
    10167,
    10168,
    10169,
    10170,
    10270,
}

Creature.roam_rooms = {
    10166,
    10167,
    10168,
    10169,
    10170,
    10270,
}

Creature.roam_chance     = 30   -- % chance to move each tick
Creature.respawn_seconds = 150
Creature.max_count       = 1

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Smaller than a dwarf and even many halflings, the kobold has ruddy skin and a hairless pate topped with small horns.  Long-limbed for its size, it eschews brute strength and relies on what agility it can pretend to possess.  Its beady little black eyes size you up with improbable calculation."

return Creature
