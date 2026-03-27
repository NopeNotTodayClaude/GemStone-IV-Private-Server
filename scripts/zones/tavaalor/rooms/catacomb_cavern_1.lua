-- Room 5917: Catacombs, Cavern
local Room = {}

Room.id          = 5917
Room.zone_id     = 2
Room.title       = "Catacombs, Cavern"
Room.description = "A slight breeze stirs the silken-threads of a monstrous cobweb, which almost entirely hides the eastern wall."

Room.exits = {
    climb_ladder         = 5916,
    north                = 5918,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
