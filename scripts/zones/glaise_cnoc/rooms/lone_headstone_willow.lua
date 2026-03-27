-- Room 5838: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5838
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A lone headstone sits in the shade of a towering willow tree.  A gentle breeze rustles the long narrow leaves of the willow as its tendrils reach toward the ground.  Drooping branches from the tree's large canopy extend over the path, providing shade."

Room.exits = {
    southwest                = 5837,
    northeast                = 5839,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
