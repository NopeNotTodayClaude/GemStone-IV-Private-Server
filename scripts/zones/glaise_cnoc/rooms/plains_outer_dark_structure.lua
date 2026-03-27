-- Room 10713: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10713
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Looking over the inner wall to the northwest, the top of a dark structure can be seen.  To the west, the walls continue to parallel one another, each wall as straight as an elven-made arrow.  Wooden guy-poles have been placed to reinforce the outer wall.  Moonlight does not do much to improve the look of the area.  A few of the poles have rotted into useless bits of wood, but most remain firmly in place."

Room.exits = {
    northeast                = 10712,
    west                     = 10714,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
