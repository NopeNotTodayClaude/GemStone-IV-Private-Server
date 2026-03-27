-- Room 10679: Glaise Cnoc, Cenotaph
local Room = {}

Room.id          = 10679
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cenotaph"
Room.description = "In the dim light, this mausoleum appears to be completely empty.  As your eyes adjust to the darkness, a plaque becomes visible on the eastern wall.  The air inside the mausoleum is cool and musty."

Room.exits = {
    out                      = 5859,
}

Room.indoor      = true
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
