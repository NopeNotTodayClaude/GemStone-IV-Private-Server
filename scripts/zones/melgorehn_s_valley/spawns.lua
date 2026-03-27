-- Melgorehn's Valley Spawn Registry
local Spawns={}
Spawns.zone="melgorehn_s_valley"; Spawns.area="Melgorehn's Valley"
Spawns.room_range={min=3758,max=7964}
Spawns.population = {
    { mob="lesser_burrow_orc", level=7, max=6, depth="valley_entry" },
    { mob="greater_burrow_orc", level=8, max=5, depth="valley_deep" },
}
return Spawns
