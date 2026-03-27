-- Room 10700: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10700
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "To the south, a wide pit stretches almost completely between the two walls.  It's difficult to tell the depth of the pit due to the night blackness.  A thick wooden plank stretches to the other side of the pit.  Cracks in the plank question the sturdiness of the makeshift bridge.  Looking to the north, the outer wall has been knocked in half, the rubble scattered across the pathway."

Room.exits = {
    north                    = 10699,
    south                    = 10701,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
