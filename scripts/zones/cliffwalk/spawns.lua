-- Cliffwalk Spawn Registry
local Spawns={}
Spawns.zone="cliffwalk"; Spawns.area="Cliffwalk"
Spawns.room_range={min=29120,max=29226}
Spawns.map_locked = true
Spawns.population = {
    { mob="shelfae_guard", level=7, max=5, depth="cliffwalk_mid" },
    { mob="crazed_canine", level=10, max=5, depth="cliffwalk_lower" },
}





Spawns.mob_rooms = {
    shelfae_guard = {
        29120, 29124, 29128, 29129, 29131, 29133, 29134, 29217, 29218, 29219,
        29220, 29221, 29222
    },
    crazed_canine = {
        29120, 29124, 29128, 29129, 29131, 29133, 29134, 29217, 29218, 29219,
        29220, 29221, 29222
    },
}

return Spawns
