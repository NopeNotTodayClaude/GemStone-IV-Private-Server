-- Room 10706: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10706
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A dead tree lies between the walls, its branches resting on the inner wall.  A few stones have been pushed from the inner wall, providing small glimpses by moonlight into the area beyond."

Room.exits = {
    east                     = 10707,
    west                     = 10705,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
