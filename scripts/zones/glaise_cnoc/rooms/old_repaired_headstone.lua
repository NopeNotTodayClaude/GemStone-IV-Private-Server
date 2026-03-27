-- Room 5877: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5877
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Sunlight streams down upon an old headstone on the north side of the path.  The headstone is chipped and worn.  Pieces of marble appear to have been painstakingly cemented in place, with a simple mortar.  A young oak tree grows alongside the charred stump of what once may have been its parent."

Room.exits = {
    go_arbor                 = 10683,  -- west approach to arbor
    east                     = 5876,
    west                     = 5878,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
