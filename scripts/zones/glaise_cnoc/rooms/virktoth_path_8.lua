-- Room 10737: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10737
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The stair continues at a gentle slope.  Hairline cracks fan out from the center of several of the steps.  Other than the cracks, no other damage is apparent to the steps.  Moonlight washes over the stairway, bathing everything around in its pale glow."

Room.exits = {
    southeast                = 10738,
    northwest                = 10736,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
