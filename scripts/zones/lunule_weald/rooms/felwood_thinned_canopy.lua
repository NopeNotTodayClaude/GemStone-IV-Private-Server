-- Room 10568: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10568
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "The forest canopy above has thinned out considerably.  Many of the trees here appear to be dead, their rotting leaves and limbs covering the forest floor.  Several dead branches have fallen and are caught precariously in the branches of other trees."

Room.exits = {
    east                     = 10567,
    southwest                = 10569,
    west                     = 10576,
    north                    = 10577,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
