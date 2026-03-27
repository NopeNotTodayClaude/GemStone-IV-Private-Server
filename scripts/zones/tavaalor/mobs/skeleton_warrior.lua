-- Creature: skeleton warrior
-- Zone: tavaalor | Catacombs | Level: 5
-- Source: gswiki.play.net/Skeleton_warrior
--
-- Ancient Vaalor soldiers entombed beneath the city, still armed and
-- wearing the remnants of their military equipment.  Far more dangerous
-- than lesser skeletons due to their martial training (reflected in higher
-- AS/DS) and chain mail equivalent armor.
--
-- The crumble and decay message references their distinctive armor clanging
-- apart — a signature sound that veterans associate with a safe kill.
--
-- GS4 Canon Stats (Level 5):
--   HP: ~60      AS (broadsword): 62   AS (fist): 52
--   DS: 52       Bolt DS: 35           TD: 15
--   ASG: 5 (chain mail — not natural, carried from entombment)
--   Experience: ~150 base exp per kill
--   Undead: immune to poison/disease, resist cold
-- -----------------------------------------------------------------------
local Creature = {}

Creature.id             = 7004
Creature.name           = "skeleton warrior"
Creature.level          = 5
Creature.family         = "skeleton"
Creature.classification = "corporeal_undead"
Creature.body_type      = "biped"

-- ── Vitals ───────────────────────────────────────────────────────────────
Creature.hp_base        = 58
Creature.hp_variance    = 8

-- ── Combat ───────────────────────────────────────────────────────────────
-- Armed with a burial broadsword (rusted but still deadly).
-- Will fall back to closed-fist smashes if unarmed.
Creature.ds_melee       = 52
Creature.ds_bolt        = 35
Creature.td_spiritual   = 15
Creature.td_elemental   = 15
Creature.udf            = 0
Creature.armor_asg      = 5      -- ASG 5: full chain mail (entombed with it)
Creature.armor_natural  = false  -- worn armor, not natural — can be stripped by spells

Creature.attacks = {
    { type = "broadsword",  as = 62, damage_type = "slash",    weight = 65 },
    { type = "closed_fist", as = 52, damage_type = "crush",    weight = 25 },
    { type = "shield_bash", as = 48, damage_type = "crush",    weight = 10 },
}

Creature.spells    = {}
Creature.abilities = {}

Creature.immune = { "poison", "disease" }
Creature.resist = { "cold" }

-- ── Loot ─────────────────────────────────────────────────────────────────
-- Level 5 undead: consistent coin drop, decent box/gem chance.
-- Skin is a crumbling iron helm — salvageable military equipment.
Creature.loot_coins   = true     -- 20-80 silver coins
Creature.loot_gems    = true     -- ~20% gem drop (clear zircon, small yellow sapphire)
Creature.loot_magic   = true     -- ~5% minor magic item (old scroll, wand fragment)
Creature.loot_boxes   = true     -- ~25% locked box
Creature.skin         = "a crumbling iron helm"
Creature.special_loot = {
    "a tarnished vaalor signet ring",  -- ~8% drop, historical/quest flavor
}

-- ── Decay ─────────────────────────────────────────────────────────────────
Creature.decay_seconds = 240
Creature.crumbles      = true
Creature.decay_message = "The skeleton warrior's armor clangs loudly as its animating force fails and its bones scatter across the floor."

-- ── Description ──────────────────────────────────────────────────────────
Creature.description = "The skeleton warrior stands straight-backed even in undeath, a grim mockery of its former military bearing.  Rusted chain mail hangs from its bones in ragged loops, and a tarnished broadsword is clutched in its yellowed fist.  The crest on its battered helm is still recognizable as the ancient Vaalor sigil."

-- ── Spawn Rooms ───────────────────────────────────────────────────────────
-- Deep rooms only.  Skeleton warriors represent the entombed elite of the
-- old garrison — their burial chambers are the deepest and most fortified
-- sections: Crypt, Trophy Room, Burial Chamber, Nexus, Serpent's Den, Lair.
Creature.spawn_rooms = {
    -- Not yet assigned: zone not built out
}

Creature.roam_rooms = {
    -- Not yet assigned
}

Creature.roam_chance     = 15    -- disciplined: does not wander far from post
Creature.respawn_seconds = 280
Creature.max_count       = 6

return Creature
