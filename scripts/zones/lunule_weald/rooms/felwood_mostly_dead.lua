-- Room 10566: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10566
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "There are more dead trees than living ones.  The saplings that once struggled for life lay dead and dying on the forest floor.  Littering the path are the rotting remains of the once living trees.  The trees that do live, appear to be dying, their leaves various shades of brown, their branches broken or breaking."

Room.exits = {
    north                    = 10565,
    south                    = 10567,
    west                     = 10577,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
