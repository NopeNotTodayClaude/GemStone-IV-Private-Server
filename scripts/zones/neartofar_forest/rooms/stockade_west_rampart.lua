-- Room 10666: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10666
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "The view over the parapet shows the western approach to the stockade.  The stumps in the grassy field appear at regular distances, as if to mark the range from the outer wall.  A low inner wall looks out over the courtyard below, its crenelated top allowing defenders to resist an attack from within the compound."

Room.exits = {
    down                     = 10665,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
