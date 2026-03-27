-- Room 10579: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10579
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "The forest floor is littered with dead branches, leaves and saplings.  There are no leaves on the tall, dark trees, their branches split and rotting.  Moonlight filters in from above, as the once lush, thick forest canopy is now brown and falling like rotting snow to the ground."

Room.exits = {
    west                     = 10578,
    south                    = 10580,
    southwest                = 10581,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
