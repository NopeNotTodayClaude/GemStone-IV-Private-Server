-- Room 5921: Catacombs, Landfill
local Room = {}

Room.id          = 5921
Room.zone_id     = 2
Room.title       = "Catacombs, Landfill"
Room.description = "Various refuse litters the floor, discarded from the city street above."

Room.exits = {
    south                = 5920,
    north                = 5922,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
