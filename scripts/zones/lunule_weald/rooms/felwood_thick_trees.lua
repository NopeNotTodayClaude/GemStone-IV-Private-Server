-- Room 10569: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10569
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "It is difficult to find a straight path through the thick, dark trees.  The forest floor is covered with dead, decaying leaves, branches and mushrooms, and the air is still and silent.  The smell of rotting vegetation pervades the area."

Room.exits = {
    northeast                = 10568,
    southwest                = 10570,
    northwest                = 10576,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
