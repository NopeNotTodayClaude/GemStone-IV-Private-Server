-- Room 10567: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10567
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "A large tree has fallen upon its side, its dead branches, leaves and moss litter the forest floor.  Painted and carved into the smooth trunk are letters that form no words and symbols and shapes of all sizes.  The dead trunk is home to a plethora of insects, worms and fungi."

Room.exits = {
    north                    = 10566,
    west                     = 10568,
    go_tree                  = 10578,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
