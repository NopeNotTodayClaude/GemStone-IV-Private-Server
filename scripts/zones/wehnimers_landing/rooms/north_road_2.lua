-- Room 118: North Road, Residential
local Room = {}

Room.id          = 118
Room.zone_id     = 1
Room.title       = "North Road"
Room.description = "The cobblestone road continues northward through a quieter residential section of town.  Modest stone and timber homes line the street, their small yards bordered by low stone walls.  Smoke curls from chimneys, and the occasional dog barks from behind a fence."

Room.exits = {
    south     = 109,
    north     = 115,
}

Room.indoor = false
Room.safe   = true

return Room
