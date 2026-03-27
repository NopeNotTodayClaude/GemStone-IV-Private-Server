-- Room 10657: Neartofar Forest, Hillside
local Room = {}

Room.id          = 10657
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Hillside"
Room.description = "A trench leads out from the stockade wall and leads down the grassy hillside.  Some lovely white calla lilies grow on the side of the trench, oblivious to the stench that rises from its depths.  Farther down the hillside, the charred stumps of several trees can still be seen rising above the trampled grass."

Room.exits = {
    southeast                = 10643,
    west                     = 10650,
    northeast                = 10656,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
