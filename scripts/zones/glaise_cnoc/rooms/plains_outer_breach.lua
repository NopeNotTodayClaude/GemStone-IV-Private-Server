-- Room 10694: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10694
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A breach in the outer wall opens up onto a small trail that heads towards a thick stand of trees.  Rubble is strewn throughout the area, most of it inside the walls, now a hazard to those walking through the area.  A rusted iron chain spans the breach in the wall, its purpose not readily apparent."

Room.exits = {
    east                     = 10695,
    west                     = 10715,
    go_breach                = 5851,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
