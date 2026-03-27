-- Room 10603: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10603
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Rocks of all shapes and sizes surround a small square of soil that appears to have once been a household garden.  The garden rows are full of rotting leaves and decaying vegetation, a myriad of mushrooms are the only things growing here.  A large dead tree stands guard over the simple plot of decay and fungi."

Room.exits = {
    north                    = 10601,
    northeast                = 10602,
    south                    = 10620,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
