-- Room 5862: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5862
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A low boxwood hedge encloses a small plot.  Neatly trimmed, the hedge is cut low allowing a clear view of the simple granite headstone within.  A pair of birds perched in a nearby linden tree trill softly, their song carried clearly on a gentle breeze."

Room.exits = {
    northwest                = 5861,
    southeast                = 5863,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
