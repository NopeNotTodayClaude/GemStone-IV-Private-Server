-- Room 31483: Oceanside Forest, Clearing
local Room = {}

Room.id          = 31483
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Clearing"
Room.description = "Sounds of the sea fill the clearing with the crashing tones of ocean waves.  As the trail winds around a tall stone circle, the way is covered with small pebbles, shells, and sand.  Caught behind the enclosing ring of granite, a towering lasimor tree spreads its branches upwards, its crimson leaves a beacon in the sky."

Room.exits = {
    west                     = 31482,
    east                     = 31484,
    go_archway               = 31519,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
