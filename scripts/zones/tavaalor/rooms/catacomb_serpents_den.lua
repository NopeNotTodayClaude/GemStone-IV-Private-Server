-- Room 5934: Catacombs, Serpent's Den
local Room = {}

Room.id          = 5934
Room.zone_id     = 2
Room.title       = "Catacombs, Serpent's Den"
Room.description = "A huge snake pit dominates this area.  Near the pit lies a pool of murky water filled with more snakes.  It is impossible to determine which direction the reptiles are moving as they splash in the foul smelling fluid."

Room.exits = {
    southeast            = 5933,
    northwest            = 5935,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
