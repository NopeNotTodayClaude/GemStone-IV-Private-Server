-- Melgorehn's Valley Spawn Registry
local Spawns={}
Spawns.zone="melgorehn_s_valley"; Spawns.area="Melgorehn's Valley"
Spawns.room_range={min=3758,max=7964}
Spawns.map_locked = true
Spawns.population = {
    { mob="lesser_burrow_orc", level=7, max=6, depth="valley_entry" },
    { mob="greater_burrow_orc", level=8, max=5, depth="valley_deep" },
}





Spawns.mob_rooms = {
    lesser_burrow_orc = {
        3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3766, 3767,
        3768, 3769, 3770, 3771, 3772
    },
    greater_burrow_orc = {
        3773, 3774, 3775, 3776, 3777, 3778, 3779, 3780, 3781, 3782,
        3783, 3784, 3785, 3786, 3787
    },
}

return Spawns
