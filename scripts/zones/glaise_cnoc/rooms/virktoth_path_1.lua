-- Room 10730: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10730
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The steps continue up a gentle incline to the west.  The glazed steps are still perfectly smooth, a testament to their obviously magical creation.  A few humanoid skulls have been scattered along the steps, each staring up into the star-filled sky."

Room.exits = {
    east                     = 10729,
    west                     = 10731,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
