-- Room 5930: Catacombs, Burial Chamber
local Room = {}

Room.id          = 5930
Room.zone_id     = 2
Room.title       = "Catacombs, Burial Chamber"
Room.description = "This corner of the cavern is bigger and oddly cleaner than the rest of the catacombs."

Room.exits = {
    west                 = 5929,
    northwest            = 5931,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
