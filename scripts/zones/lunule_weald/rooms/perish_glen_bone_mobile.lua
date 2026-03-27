-- Room 10593: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10593
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "As the howling wind blows through the branches of the dead trees, their remaining leaves float gently to the ground to join in the decay and rot of the forest floor.  Tied to a high branch in one of the trees is a small mobile, the little bones tinkling softly as they bump against each other in the breeze."

Room.exits = {
    northeast                = 10589,
    northwest                = 10592,
    southeast                = 10594,
    southwest                = 10610,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
