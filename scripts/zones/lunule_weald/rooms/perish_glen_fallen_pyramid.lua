-- Room 10587: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10587
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "Three dead trees have fallen into each other, forming a standing pyramid of rotting wood.  Decaying vegetation, branches and fungi have formed a nest of putrid compost inside the pyramid formation.  The repugnant smell is overpowering."

Room.exits = {
    east                     = 10585,
    southeast                = 10586,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
