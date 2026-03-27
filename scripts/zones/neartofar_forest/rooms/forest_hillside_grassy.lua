-- Room 10656: Neartofar Forest, Hillside
local Room = {}

Room.id          = 10656
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Hillside"
Room.description = "The expansive grassy hillside somehow renders the forest beyond the tree line more threatening, as the trees hide the threats that lurk therein.  Cold comfort lies in the other direction, where the malevolent structure of the wooden stockade boldly declares its defenders' presence and hostile intent.  A cold wind whisks across the hillside, barely stirring the grass that was trampled by legions unknown."

Room.exits = {
    southeast                = 10644,
    north                    = 10653,
    southwest                = 10657,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
