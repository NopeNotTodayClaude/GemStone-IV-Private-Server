-- Creature: gnoll worker
-- Zone: Upper Trollfang / Mountain Foothills  |  Level: 10
local Creature = {}
Creature.id              = 9407
Creature.name            = "gnoll worker"
Creature.level           = 10
Creature.family          = "gnoll"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 132
Creature.hp_variance     = 10
Creature.ds_melee        = 96
Creature.ds_bolt         = 45
Creature.td_spiritual    = 32
Creature.td_elemental    = 32
Creature.udf             = 0
Creature.armor_asg       = 8
Creature.armor_natural   = false
Creature.attacks = {
    { type="flail", as=136, damage_type="crush" },
    { type="handaxe", as=130, damage_type="slash" },
}
Creature.spells = {}
Creature.abilities = {}
Creature.immune    = {}
Creature.resist    = {}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a gnoll hide"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    1277,
    1278,
    1279,
    1280,
    1281,
    1282,
    1283,
    1284,
    1285,
    1286,
    1287,
    1288,
    1289,
    1290,
    1291,
    1292
    }
Creature.roam_rooms = {
    1277,
    1278,
    1279,
    1280,
    1281,
    1282,
    1283,
    1284,
    1285,
    1286,
    1287,
    1288,
    1289,
    1290,
    1291,
    1292,
    4106,
    4107,
    4108
    }
Creature.roam_chance     = 20
Creature.respawn_seconds = 280
Creature.max_count       = 2
Creature.description = "Hyena-headed and with the stooped gait of its kind, the gnoll worker is the backbone of gnoll society — and by extension its military, since gnolls make little distinction between labor and warfare.  Spotted fur covers a powerfully-built frame, and the laugh-like vocalization it makes while attacking is genuinely unsettling."
return Creature
