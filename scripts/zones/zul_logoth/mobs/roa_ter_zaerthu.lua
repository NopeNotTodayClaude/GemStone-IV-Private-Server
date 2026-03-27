-- Creature: Roa'ter
-- Zone: Zul Logoth / Zaerthu Tunnels  |  Level: 24
local Creature = {}
Creature.id              = 10403
Creature.name            = "Roa'ter"
Creature.level           = 24
Creature.family          = "roa_ter"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 295
Creature.hp_variance     = 24
Creature.ds_melee        = 205
Creature.ds_bolt         = 98
Creature.td_spiritual    = 76
Creature.td_elemental    = 76
Creature.udf             = 8
Creature.armor_asg       = 10
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=290, damage_type="puncture" },
    { type="claw", as=282, damage_type="slash" },
    { type="acid_spray", as=272, damage_type="fire" },
}
Creature.spells          = {}
Creature.abilities       = {
    "acid_spray",
    "tunnel_sight",
    "armoured_carapace",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a Roa'ter carapace plate"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    5787,
    5788,
    5789,
    5790,
    5791,
    5792,
    5793,
    5794,
    5795,
    5796,
    5797,
    5798,
    5799,
    5800,
    5801,
    5802,
    5803,
    5804,
    5805,
    5806
    }
Creature.roam_rooms      = {
    5787,
    5788,
    5789,
    5790,
    5791,
    5792,
    5793,
    5794,
    5795,
    5796,
    5797,
    5798,
    5799,
    5800,
    5801,
    5802,
    5803,
    5804,
    5805,
    5806
    }
Creature.roam_chance     = 18
Creature.respawn_seconds = 420
Creature.max_count       = 3
Creature.description     = "The Roa'ter is a quadrupedal tunnel-dweller with a carapace of fused stone-like plates across its dorsal surface and a jaw structure capable of exerting enormous pressure.  It navigates entirely by echolocation and chemical sensing, which means blindness magic is ineffective as a tactical option.  The acid gland near the tail can project a corrosive spray at close range."
return Creature
