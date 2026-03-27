-- Room 5915: Catacombs, Storage Room
local Room = {}

Room.id          = 5915
Room.zone_id     = 2
Room.title       = "Catacombs, Storage Room"
Room.description = "A stockpile of the mutant mushrooms reaches the ceiling in this chamber."

Room.exits = {
    go_door              = 5914,
    east                 = 5916,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
