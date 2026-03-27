-- Muddy Village Spawn Registry
local Spawns={}
Spawns.zone="muddy_village"; Spawns.area="Muddy Village"
Spawns.room_range={min=29047,max=29076}
Spawns.population = {
    { mob="monkey", level=6, max=7, depth="village_commons" },
    { mob="hobgoblin_acolyte", level=7, max=5, depth="village_deep" },
}
return Spawns
