-- Room 5858: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5858
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path rises to the south as it climbs a verdant knoll.  Sunlight streams down upon two large, identical headstones which provide a backdrop for a pair of pewter grave markers inset in the ground, in what appears to be a family plot.  A marble and pewter plaque has been placed in the center of the four markers."

Room.exits = {
    northeast                = 5857,
    south                    = 5859,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
