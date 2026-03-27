-- Room 10562: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10562
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "A small piece of indeterminable material is tangled in the moss in a high branch of one of the trees.  Hanging from the material by thin pieces of twine are several metal crescent moon shapes that tinkle softly as they hit each other."

Room.exits = {
    southwest                = 10561,
    northeast                = 10563,
    south                    = 10573,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
