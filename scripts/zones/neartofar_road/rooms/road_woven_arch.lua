-- Room 31455: Neartofar Road
local Room = {}

Room.id          = 31455
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Snaking through the dense woodland, the coarse roadway is protected by a naturally woven arch of leaf-covered branches.  Thick bushes and greenery flourish in the moist ground around the bases of the tall sentinels.  Here and there, bright rays of sunlight penetrate the canopy, illuminating clusters of cinnamon ferns and some stalks of snakeroot."

Room.exits = {
    northwest                = 31454,
    east                     = 31456,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
