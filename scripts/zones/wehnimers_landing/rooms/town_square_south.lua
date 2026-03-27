-- Room 102: Town Square, South
local Room = {}

Room.id          = 102
Room.zone_id     = 1
Room.title       = "Town Square, South"
Room.description = "The southern end of the square gives way to a wide dirt road stretching toward the south gate of town.  A weathered wooden signpost marks the crossroads, its arms pointing in several directions.  The smell of the harbor drifts in on a salty breeze."

Room.exits = {
    north     = 100,
    south     = 110,
    east      = 107,
    west      = 108,
}

Room.indoor = false
Room.safe   = true

return Room
