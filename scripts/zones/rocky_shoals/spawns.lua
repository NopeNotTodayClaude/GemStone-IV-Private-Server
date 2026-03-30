-- Rocky Shoals Spawn Registry
local Spawns={}
Spawns.zone="rocky_shoals"; Spawns.area="Rocky Shoals"
Spawns.room_range={min=29135,max=29216}
Spawns.map_locked = true
Spawns.population = {
    { mob="coconut_crab", level=2, max=8, depth="shoals_beach" },
}





Spawns.mob_rooms = {
    coconut_crab = {
        29188, 29189, 29190, 29191, 29192, 29193, 29194, 29195, 29196, 29197,
        29198, 29199, 29200
    },
}

return Spawns
