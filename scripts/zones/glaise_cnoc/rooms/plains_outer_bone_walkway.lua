-- Room 10710: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10710
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Humanoid leg bones have been laid together to form a walkway between the walls.  A few of the bones have been jarred out of place and now present hazards to travellers.  The outer wall bulges out slightly as if rammed from the inside.  The night mist hangs low to the ground, swirling with the slightest disturbance."

Room.exits = {
    north                    = 10709,
    south                    = 10711,
    go_hole                  = 10716,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
