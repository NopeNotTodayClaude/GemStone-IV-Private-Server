-- Creature: troglodyte
-- Zone: wehnimers_landing / Wehnimer's Environs (Trollfang entry)  |  Level: 3
-- Source: https://gswiki.play.net/Troglodyte
-- HP: 60 | AS: 68 (cudgel) | DS: 26 | bolt: 11 | UDF: 44 | TD: 9
-- ASG: 5 (light leather) | Treasure: coins yes, gems yes, boxes yes | Skin: troglodyte hide
local Creature = {}

Creature.id              = 9325
Creature.name            = "troglodyte"
Creature.level           = 3
Creature.family          = "humanoid"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 60
Creature.hp_variance     = 6

-- ── Combat ────────────────────────────────────────────────────────────────
Creature.ds_melee        = 26
Creature.ds_bolt         = 11
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 44
Creature.armor_asg       = 5
Creature.armor_natural   = false

Creature.attacks = {
    { type = "staff", as = 68, damage_type = "crush" },
}

Creature.spells    = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}

-- ── Loot ─────────────────────────────────────────────────────────────────
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a troglodyte hide"
Creature.special_loot = {}

-- ── Decay / Death Behavior ────────────────────────────────────────────────
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

-- ── Spawn & Roam Restrictions ─────────────────────────────────────────────
-- Trollfang entry area. Troglodytes lurk at the cave mouths and rocky
-- outcroppings. Hard cap — they do not venture into deeper trollfang.
Creature.spawn_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
}

Creature.roam_rooms = {
    452, 453, 454, 455,
    456, 457, 458, 459,
    460, 461, 462, 463,
    464, 465, 466, 467,
    468, 469, 470, 471,
}

Creature.roam_chance     = 20
Creature.respawn_seconds = 200
Creature.max_count       = 2

-- ── Ambient / Flavor ──────────────────────────────────────────────────────
Creature.description = "Hunched and cave-pale, the troglodyte's long arms drag the knuckles of one hand along the ground while the other grips a heavy cudgel with practiced ease.  Its wide, lipless mouth opens and closes rhythmically, and the musk it produces is an assault in itself.  It navigates darkness with unsettling confidence."

return Creature
