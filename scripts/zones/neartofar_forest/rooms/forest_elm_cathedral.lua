-- Room 10626: Neartofar Forest
local Room = {}

Room.id          = 10626
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A ring of elm trees circles a grove of shorter oaks, their massive limbs reaching out in a leafy embrace.  The curious growth resembles an arboreal cathedral, with a canopy of elms supported by sturdy columns of oak.  The trees maintain a respectful silence broken only by the sound of wind rushing through the leaves high above."

Room.exits = {
    northwest                = 10625,
    southeast                = 10627,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
