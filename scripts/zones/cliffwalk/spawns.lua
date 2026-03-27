-- Cliffwalk Spawn Registry
local Spawns={}
Spawns.zone="cliffwalk"; Spawns.area="Cliffwalk"
Spawns.room_range={min=29120,max=29226}
Spawns.population = {
    { mob="shelfae_guard", level=7, max=5, depth="cliffwalk_mid" },
    { mob="crazed_canine", level=10, max=5, depth="cliffwalk_lower" },
}
return Spawns
