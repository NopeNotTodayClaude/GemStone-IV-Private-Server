-- Room 101: Town Square, North
local Room = {}

Room.id          = 101
Room.zone_id     = 1
Room.title       = "Town Square, North"
Room.description = "The northern edge of the town square opens toward a wide cobblestone road leading further into the heart of the town.  A large stone building bearing the crest of the town guard stands to the northwest.  Several benches line the square, occupied by resting townsfolk and the occasional adventurer."

Room.exits = {
    south     = 100,
    north     = 109,
    east      = 105,
    west      = 106,
    go_building = 120,
}

Room.indoor = false
Room.safe   = true

return Room
