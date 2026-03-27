-- Creature: Grutik shaman
-- Zone: Zul Logoth / Zaerthu Tunnels  |  Level: 29
local Creature = {}
Creature.id              = 10402
Creature.name            = "Grutik shaman"
Creature.level           = 29
Creature.family          = "grutik"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 355
Creature.hp_variance     = 29
Creature.ds_melee        = 240
Creature.ds_bolt         = 118
Creature.td_spiritual    = 92
Creature.td_elemental    = 92
Creature.udf             = 0
Creature.armor_asg       = 5
Creature.armor_natural   = false
Creature.attacks         = {
    { type="staff", as=345, damage_type="crush" },
    { type="claw", as=336, damage_type="slash" },
}
Creature.spells          = {
    { name="earth_shatter", cs=145, as=0 },
    { name="stone_bolt", cs=140, as=0 },
    { name="curse", cs=135, as=0 },
}
Creature.abilities       = {
    "tunnel_sight",
    "stone_call",
    "earth_ward",
    "aura_of_earth",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = true
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = true
Creature.skin            = "a Grutik shaman totem"
Creature.special_loot    = {
    "a carved stone fetish",
    "a Grutik ritual bone",
}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
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
    5806,
    5807,
    5808,
    5809,
    5810,
    5811
    }
Creature.roam_rooms      = {
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
    5806,
    5807,
    5808,
    5809,
    5810,
    5811
    }
Creature.roam_chance     = 15
Creature.respawn_seconds = 540
Creature.max_count       = 2
Creature.description     = "Robed in layers of cave moss and hung with carved stone fetishes, the Grutik shaman holds spiritual authority in the tunnel community that translates directly into combat advantage.  The magic it works is earth-magic — stone and tunnel and subsurface pressure — and in the tunnels of Zaerthu this is home territory.  The staff carries a head carved from a single piece of bloodstone."
return Creature
