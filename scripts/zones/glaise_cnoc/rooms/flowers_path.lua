-- Room 5892: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5892
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Flowers of several varieties line the gravel path, their petals shining brightly in the sunlight.  Lavender, yellow, pink and blue blooms reach for the sky, their delicate perfume filling the air.  Fat bumblebees hover above the flowers, drinking their sweet nectar."

Room.exits = {
    north                    = 24559,
    south                    = 5879,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
