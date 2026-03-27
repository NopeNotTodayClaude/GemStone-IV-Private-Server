-- Room 5931: Catacombs, Nexus
local Room = {}

Room.id          = 5931
Room.zone_id     = 2
Room.title       = "Catacombs, Nexus"
Room.description = "All of the pipes seem to empty out into this general area, and large amounts of rancid water are unavoidable."

Room.exits = {
    south                = 5929,
    southeast            = 5930,
    northwest            = 5932,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
