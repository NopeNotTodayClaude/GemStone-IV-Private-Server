-- Room 59001: Tutorial - Misty Path
-- Teaches: basic movement (north, south, look)

local Room = {}

Room.id          = 59001
Room.zone_id     = 99
Room.title       = "A Misty Path"
Room.description = "A narrow path of pale stone winds through the mist.  Strange flowers with luminous petals grow along the edges, casting soft light across the ground.  The path continues north, where the mist seems to thin slightly."

Room.exits = {
    south = 59000,
    north = 59002,
}

Room.indoor = false
Room.safe   = true

return Room
