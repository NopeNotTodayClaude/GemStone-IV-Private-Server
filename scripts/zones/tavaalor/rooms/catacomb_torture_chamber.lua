-- Room 5923: Catacombs, Torture Chamber
local Room = {}

Room.id          = 5923
Room.zone_id     = 2
Room.title       = "Catacombs, Torture Chamber"
Room.description = "Dozens of sharp metallic spikes protrude from the walls, and impaled on three of them are the mummified, humanoid remains of two males and one female."

Room.exits = {
    south                = 5922,
    north                = 5924,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
