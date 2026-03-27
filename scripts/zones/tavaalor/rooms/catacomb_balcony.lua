-- Room 5940: Catacombs, Balcony
local Room = {}

Room.id          = 5940
Room.zone_id     = 2
Room.title       = "Catacombs, Balcony"
Room.description = "Thick, clear slimy stuff covers both walls and floor in the room."

Room.exits = {
    northeast            = 5939,
    southwest            = 5941,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
