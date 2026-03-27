-- Room 10738: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10738
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The stairway turns sharply here, some of the steps so short that they can only serve as toe-holds.  A few bones protrude from the hill into the black sky, aids during this treacherous portion of the stair.  A small bird nest is tucked into the corner of one step."

Room.exits = {
    northeast                = 10739,
    northwest                = 10737,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
