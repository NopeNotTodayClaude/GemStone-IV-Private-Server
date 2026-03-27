-- Room 5911: Catacombs, Tunnels
local Room = {}

Room.id          = 5911
Room.zone_id     = 2
Room.title       = "Catacombs, Tunnels"
Room.description = "Muffled sounds from the city above provide some comfort in this section of the sewer."

Room.exits = {
    north                = 5910,
    south                = 5912,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
