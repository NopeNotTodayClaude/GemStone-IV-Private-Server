-- Room 10617: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10617
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "A small shack leans precariously to one side, its thatch roof consumed by rot long ago.  One of the walls has crumbled and fallen into the remaining walls, forcing them to lean in at an odd angle.  The door lays on the ground covered in dead leaves, dirt and mushrooms.  The signs of long ago violence are still present on the rusted hinges, which are bent at odd angles and point accusingly at nothing."

Room.exits = {
    south                    = 10599,
    southeast                = 10604,
    southwest                = 10618,
    northwest                = 10619,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
