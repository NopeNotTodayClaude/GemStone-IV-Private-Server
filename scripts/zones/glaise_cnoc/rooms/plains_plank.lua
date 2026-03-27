-- Room 10699: Plains of Bone, Plank
local Room = {}

Room.id          = 10699
Room.zone_id     = 3
Room.title       = "Plains of Bone, Plank"
Room.description = "Looking downward, only blackness and bones can be seen.  Cobwebs dangle from the bottom of the plank, glistening with moisture in the moonlight, along with decaying leaves that have been caught up in the webs.  The plank ends not far to the north."

Room.exits = {
    north                    = 10698,
    south                    = 10700,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
