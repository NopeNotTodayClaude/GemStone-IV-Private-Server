-- Creature: hobgoblin
-- Zone: the_cairnfang / The Cairnfang  |  Level: 3
-- Source: https://gswiki.play.net/Hobgoblin
local Creature = {}

Creature.id              = 9322
Creature.name            = "hobgoblin"
Creature.level           = 3
Creature.family          = "goblin"
Creature.classification  = "living"
Creature.body_type       = "biped"

Creature.hp_base         = 60
Creature.hp_variance     = 6

Creature.ds_melee        = 15
Creature.ds_bolt         = 9
Creature.td_spiritual    = 9
Creature.td_elemental    = 9
Creature.udf             = 57
Creature.armor_asg       = 7
Creature.armor_natural   = false

Creature.attacks = {
    { type = "claidhmore", as = 68, damage_type = "slash" },
    { type = "handaxe", as = 68, damage_type = "slash" },
}

Creature.spells    = {}
Creature.abilities = { "scavenge_weapon" }
Creature.immune    = {}
Creature.resist    = {}

Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a hobgoblin scalp"
Creature.special_loot = {}

Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""

Creature.spawn_rooms = {
    1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381,
    1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391,
    1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401,
    1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411,
    1412, 1413, 1414
}

Creature.roam_rooms = {
    1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381,
    1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391,
    1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401,
    1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411,
    1412, 1413, 1414
}

Creature.roam_chance     = 30
Creature.respawn_seconds = 200
Creature.max_count       = 5

Creature.description = "Larger and meaner than a goblin by an order of magnitude, the hobgoblin prowls the uplands and forest margins of the Cairnfang with the same oversized weapons and brute aggression it shows near Wehnimer's Landing."

return Creature
