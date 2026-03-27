-- Room 10650: Neartofar Forest
local Room = {}

Room.id          = 10650
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail leads through a small valley where slender birch trees sway in the breeze.  Some nesting birds call down from the high branches, as if protesting the instability of their perch.  A small footpath climbs out of the valley in the direction of the hill to the east."

Room.exits = {
    southeast                = 10649,
    northeast                = 10651,
    east                     = 10657,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
