-- Room 5935: Catacombs, Lair
local Room = {}

Room.id          = 5935
Room.zone_id     = 2
Room.title       = "Catacombs, Lair"
Room.description = "In the middle of this room lies a stack of discarded paper-thin skins."

Room.exits = {
    southeast            = 5934,
    northwest            = 5936,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
