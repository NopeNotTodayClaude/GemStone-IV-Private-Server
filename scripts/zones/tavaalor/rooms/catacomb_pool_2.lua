-- Room 5938: Catacombs, Pool
local Room = {}

Room.id          = 5938
Room.zone_id     = 2
Room.title       = "Catacombs, Pool"
Room.description = "Swimming might be easier than walking in this chamber, since it is filled with water from a broken pipe nearby.  The walls and floors are worn smooth due to the constant flow of the water.  Bodies of drowned small rodents float on the water and in one of the corners a massive collection of them are visible."

Room.exits = {
    northeast            = 5937,
    southwest            = 5939,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
