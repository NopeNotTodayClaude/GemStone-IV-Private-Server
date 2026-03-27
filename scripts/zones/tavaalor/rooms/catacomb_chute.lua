-- Room 5916: Catacombs, Chute
local Room = {}

Room.id          = 5916
Room.zone_id     = 2
Room.title       = "Catacombs, Chute"
Room.description = "In the center of the room sits a huge boulder.  In the far corner and missing several rungs, an old rickety ladder leans against the wall.  Only the portion that is eye-level is visible as the rest of it ascends upwards into total darkness."

Room.exits = {
    west                 = 5915,
    climb_ladder         = 5917,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
