-- Room 5918: Catacombs, Pool
local Room = {}

Room.id          = 5918
Room.zone_id     = 2
Room.title       = "Catacombs, Pool"
Room.description = "Cobwebs have woven themselves over humanoid remains that have been carefully placed in the niches carved into stone walls."

Room.exits = {
    south                = 5917,
    north                = 5919,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
