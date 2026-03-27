-- Room 10696: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10696
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Piles of bleached bones, glowing palely in the moonlight, lie near both walls.  The piles are an eclectic mix of bones from a bestiary of creatures.  Thick cobwebs cover the upper portions of each pile."

Room.exits = {
    east                     = 10697,
    west                     = 10695,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
