-- Room 5922: Catacombs, Tunnel
local Room = {}

Room.id          = 5922
Room.zone_id     = 2
Room.title       = "Catacombs, Tunnel"
Room.description = "Along the back wall a huge patch of skin, with matted fur still attached, clings to a jagged spot of rocks."

Room.exits = {
    south                = 5921,
    north                = 5923,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
