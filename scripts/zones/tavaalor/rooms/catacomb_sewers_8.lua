-- Room 5939: Catacombs, Sewers
local Room = {}

Room.id          = 5939
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "Hundreds of flies and maggots swarm over the remains of a massive creature, which lies partially buried in the center of this room."

Room.exits = {
    northeast            = 5938,
    southwest            = 5940,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
