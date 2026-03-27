-- Room 5841: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5841
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Four grave markers are enclosed within a low granite wall.  Tendrils of ivy weave their way along the wall, softening the harshness of the granite.  Scattered around the markers, within the confines of the wall, are small clusters of wild violets."

Room.exits = {
    southwest                = 5840,
    northeast                = 5842,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
