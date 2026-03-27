-- Room 5840: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5840
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A tall granite obelisk serves as a grave marker atop a low hillock.  Framed against the sky, it appears to touch the clouds, a lone sentinel casting its shadow over the grave it guards."

Room.exits = {
    southwest                = 5839,
    northeast                = 5841,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
