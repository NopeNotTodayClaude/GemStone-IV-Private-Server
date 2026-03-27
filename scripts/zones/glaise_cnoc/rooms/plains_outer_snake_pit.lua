-- Room 10698: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10698
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A deep pit has been dug between the two walls.  Dozens of skeletons lie in the bottom of the pit.  Snakes curl their way through the forest of bones, their scales glinting in the moonlight.  A plank spans the pit."

Room.exits = {
    northwest                = 10697,
    southeast                = 10699,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
