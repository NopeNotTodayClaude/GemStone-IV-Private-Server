-- Room 10557: Lunule Weald, Slade
local Room = {}

Room.id          = 10557
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Swarms of insects buzz loudly in the thick, humid air.  The rotting smell of the lingering patches of mud is almost palpable.  A few blades of grass defiantly force their way upward through the stinking mud."

Room.exits = {
    north                    = 10541,
    east                     = 10542,
    west                     = 10556,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
