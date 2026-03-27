-- Room 5927: Catacombs, Sewers
local Room = {}

Room.id          = 5927
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "A small cave-in happened here recently, nearly blocking the path to the west."

Room.exits = {
    west                 = 5926,
    east                 = 5928,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
