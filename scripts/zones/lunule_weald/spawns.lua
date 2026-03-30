---------------------------------------------------
-- Lunule Weald — Spawn Registry
-- scripts/zones/lunule_weald/spawns.lua
---------------------------------------------------

local Spawns = {}

Spawns.zone       = "lunule_weald"
Spawns.area       = "Lunule Weald"
Spawns.room_range = { min = 10540, max = 10621 }
Spawns.map_locked = true

Spawns.population = {
    { mob = "rotting_farmhand",   level = 13, max = 6,  depth = "slade" },
    { mob = "decaying_farmhand",  level = 14, max = 5,  depth = "slade" },
    { mob = "elder_boar",         level = 14, max = 3,  depth = "knoll" },
    { mob = "puma",               level = 15, max = 4,  depth = "knoll_felwood" },
    { mob = "decaying_woodsman",  level = 15, max = 5,  depth = "felwood_grove" },
    { mob = "fel_wolf",           level = 17, max = 5,  depth = "felwood_deep" },
    { mob = "death_dirge",        level = 18, max = 4,  depth = "perish_glen" },
    { mob = "moaning_phantom",    level = 20, max = 3,  depth = "perish_glen" },
    { mob = "arch_wight",         level = 21, max = 3,  depth = "perish_glen_deep" },
    { mob = "dark_apparition",    level = 23, max = 3,  depth = "zealot_village" },
    { mob = "shadowy_spectre",    level = 25, max = 3,  depth = "zealot_village" },
    { mob = "revenant",           level = 27, max = 2,  depth = "zealot_village_deep" },
}






Spawns.mob_rooms = {
    rotting_farmhand = {
        10540, 10541, 10542, 10543, 10544, 10548, 10549, 10550, 10551, 10556,
        10557, 10558
    },
    decaying_farmhand = {
        10540, 10541, 10542, 10543, 10544, 10548, 10549, 10550, 10551, 10556,
        10557, 10558, 10545, 10546
    },
    elder_boar = {
        10545, 10546, 10552, 10553, 10554, 10555
    },
    puma = {
        10545, 10546, 10552, 10553, 10554, 10555, 10547, 10559, 10560, 10561
    },
    decaying_woodsman = {
        10547, 10559, 10560, 10561, 10562, 10563, 10564, 10565, 10566, 10567,
        10568, 10569, 10570, 10571, 10572, 10573, 10574, 10575, 10576, 10577
    },
    fel_wolf = {
        10568, 10569, 10570, 10571, 10572, 10573, 10574, 10575, 10576, 10577,
        10578, 10579, 10580, 10581
    },
    death_dirge = {
        10578, 10579, 10580, 10581, 10582, 10583, 10584, 10585, 10586, 10587
    },
    moaning_phantom = {
        10583, 10584, 10585, 10586, 10587, 10588, 10589, 10590, 10591, 10592
    },
    arch_wight = {
        10589, 10590, 10591, 10592, 10593, 10594, 10595, 10610, 10597, 10598,
        10599
    },
    dark_apparition = {
        10597, 10598, 10599, 10600, 10601, 10602, 10603, 10604, 10605, 10606,
        10607, 10608
    },
    shadowy_spectre = {
        10605, 10606, 10607, 10608, 10609, 10611, 10612, 10613, 10614, 10615,
        10616, 10617
    },
    revenant = {
        10612, 10613, 10614, 10615, 10616, 10617, 10618, 10619, 10620, 10621
    },
}

return Spawns
