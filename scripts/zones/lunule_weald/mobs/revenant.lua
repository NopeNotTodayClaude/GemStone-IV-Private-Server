-- Creature: revenant
-- Zone: Lunule Weald / Zealot Village Deep  |  Level: 27
local Creature = {}
Creature.id              = 9512
Creature.name            = "revenant"
Creature.level           = 27
Creature.family          = "revenant"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 305
Creature.hp_variance     = 20
Creature.ds_melee        = 228
Creature.ds_bolt         = 108
Creature.td_spiritual    = 86
Creature.td_elemental    = 86
Creature.udf             = 315
Creature.armor_asg       = 13
Creature.armor_natural   = false
Creature.attacks = {
    { type="claw", as=275, damage_type="slash" },
    { type="pound", as=268, damage_type="crush" },
    { type="life_drain_touch", as=260, damage_type="cold" },
}
Creature.spells = {
    { name="wither", cs=148, as=0 },
    { name="curse", cs=142, as=0 },
    { name="spirit_servant", cs=138, as=0 },
}
Creature.abilities = {
    "wight_drain",
    "life_drain",
    "undying_purpose",
    "aura_of_dread",
    "curse_touch",
}
Creature.immune    = {
    "disease",
    "poison",
    "cold",
}
Creature.resist    = {
    "fire",
    "slash",
    "pierce",
}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a revenant talon"
Creature.special_loot = {
    "a revenant eye",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    10612,
    10613,
    10614,
    10615,
    10616,
    10617,
    10618,
    10619,
    10620,
    10621
    }
Creature.roam_rooms = {
    10612,
    10613,
    10614,
    10615,
    10616,
    10617,
    10618,
    10619,
    10620,
    10621
    }
Creature.roam_chance     = 10
Creature.respawn_seconds = 720
Creature.max_count       = 2
Creature.description = "Driven back from death by some unfinished purpose so powerful it overrode the natural order, the revenant has become something beyond the common undead.  The body is preserved in the state of death — wounds visible, face locked in the expression of its final moments — but animated by a will that is fully present and implacably focused.  It does not shamble.  It does not drift.  It walks with the deliberate purpose of something that remembers exactly who wronged it."
return Creature
