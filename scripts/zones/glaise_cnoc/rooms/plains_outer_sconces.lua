-- Room 10709: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10709
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Several sconces line this section of the inner wall.  Two of the sconces still hold torches, both in need of replacement that would be useful in the dark.  Sharpened bones cap both walls, serving as deterrents to climbing either wall."

Room.exits = {
    north                    = 10708,
    south                    = 10710,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
