-- Room 5852: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5852
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A series of nine headstones is neatly arranged in three rows of three.  The center plot in the row closest to the path appears to have been recently dug.  The freshly turned soil is a rich brown and free of grass.  The path splits here, with a trail leading towards the southeast."

Room.exits = {
    northeast                = 5851,
    southeast                = 5853,
    southwest                = 5891,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
