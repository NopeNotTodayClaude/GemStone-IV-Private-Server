-- Room 5942: Catacombs, Chart Room
local Room = {}

Room.id          = 5942
Room.zone_id     = 2
Room.title       = "Catacombs, Chart Room"
Room.description = "Ancient maps have been stashed away into a small nook in the wall."

Room.exits = {
    north                = 5941,
    west                 = 5943,
    east                 = 5944,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
