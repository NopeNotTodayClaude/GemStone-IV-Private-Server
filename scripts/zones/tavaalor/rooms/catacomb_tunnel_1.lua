-- Room 5920: Catacombs, Tunnel
local Room = {}

Room.id          = 5920
Room.zone_id     = 2
Room.title       = "Catacombs, Tunnel"
Room.description = "Stones and larger rocks are scattered across the uneven floor."

Room.exits = {
    south                = 5919,
    north                = 5921,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
