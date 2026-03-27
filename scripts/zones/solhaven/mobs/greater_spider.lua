-- Creature: greater spider
-- Zone: Vornavis / Caverns  |  Level: 8
local Creature = {}
Creature.id              = 10111
Creature.name            = "greater spider"
Creature.level           = 8
Creature.family          = "spider"
Creature.classification  = "living"
Creature.body_type       = "quadruped"
Creature.hp_base         = 115
Creature.hp_variance     = 9
Creature.ds_melee        = 78
Creature.ds_bolt         = 40
Creature.td_spiritual    = 24
Creature.td_elemental    = 24
Creature.udf             = 5
Creature.armor_asg       = 3
Creature.armor_natural   = true
Creature.attacks         = {
    { type="bite", as=112, damage_type="puncture" },
    { type="web", as=105, damage_type="unbalancing" },
}
Creature.spells          = {}
Creature.abilities       = {
    "web_trap",
    "venom_bite",
    "wall_climb",
}
Creature.immune          = {}
Creature.resist          = {}
Creature.loot_coins      = false
Creature.loot_gems       = true
Creature.loot_magic      = true
Creature.loot_boxes      = false
Creature.skin            = "a spider leg"
Creature.special_loot    = {}
Creature.decay_seconds   = 300
Creature.crumbles        = false
Creature.decay_message   = ""
Creature.spawn_rooms     = {
    7707,
    7712,
    7713,
    7714,
    7715,
    7716,
    7717,
    7718,
    7719,
    7720,
    7721,
    7722,
    7723,
    7724,
    7725,
    7726,
    7727,
    7728,
    7729,
    7730,
    7731,
    7732,
    7733,
    7734,
    7735,
    7736,
    7737,
    7738,
    7739,
    7740,
    7741,
    7742,
    7743,
    7744,
    7745,
    7746,
    7747,
    7748,
    7749,
    7750,
    7751,
    7752,
    7753,
    7754,
    7755
    }
Creature.roam_rooms      = {
    7707,
    7712,
    7713,
    7714,
    7715,
    7716,
    7717,
    7718,
    7719,
    7720,
    7721,
    7722,
    7723,
    7724,
    7725,
    7726,
    7727,
    7728,
    7729,
    7730,
    7731,
    7732,
    7733,
    7734,
    7735,
    7736,
    7737,
    7738,
    7739,
    7740,
    7741,
    7742,
    7743,
    7744,
    7745,
    7746,
    7747,
    7748,
    7749,
    7750,
    7751,
    7752,
    7753,
    7754,
    7755
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 240
Creature.max_count       = 6
Creature.description     = "Leg span approaching four feet and abdomen the size of a large melon, the greater spider has claimed significant territory in the coastal caverns.  The web it produces is of unusual strength — more like stout cord than silk — and it maintains networks of tripwire and trap-web throughout its territory.  The venom in the bite works quickly and leaves a characteristic weakness in affected muscles."
return Creature
