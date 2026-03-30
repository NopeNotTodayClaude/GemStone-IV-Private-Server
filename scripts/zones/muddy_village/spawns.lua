-- Muddy Village Spawn Registry
local Spawns={}
Spawns.zone="muddy_village"; Spawns.area="Muddy Village"
Spawns.room_range={min=29047,max=29076}
Spawns.map_locked = true
Spawns.population = {
    { mob="monkey", level=6, max=7, depth="village_commons" },
    { mob="hobgoblin_acolyte", level=7, max=5, depth="village_deep" },
}
Spawns.mob_rooms = {
    monkey = {
        29047, 29049, 29059, 29060, 29063, 29065, 29066, 29068, 29072, 29074,
        29075, 29076
    },
    hobgoblin_acolyte = {
        29061, 29062, 29064, 29067, 29069, 29070, 29071, 29073
    },
}
return Spawns
