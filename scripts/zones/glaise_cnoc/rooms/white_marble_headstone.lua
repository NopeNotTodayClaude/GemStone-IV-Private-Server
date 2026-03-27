-- Room 5865: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5865
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Beneath the gracefully oscillating branches of a willow tree sits a white marble headstone, gleaming in the sunlight that filters through the willow's branches.  The square-cut, simplistic sculpting of the headstone is elegant in its design.  Willow leaves, scattered on the ground, accent the serene resting place."

Room.exits = {
    northwest                = 5864,
    southeast                = 5866,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
