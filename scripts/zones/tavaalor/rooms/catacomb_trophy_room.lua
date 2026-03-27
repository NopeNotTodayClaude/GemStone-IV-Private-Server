-- Room 5941: Catacombs, Trophy Room
local Room = {}

Room.id          = 5941
Room.zone_id     = 2
Room.title       = "Catacombs, Trophy Room"
Room.description = "In one corner of the chamber, a table created from rocks holds a dozen human skulls."

Room.exits = {
    northeast            = 5940,
    south                = 5942,
    go_door              = 5943,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
