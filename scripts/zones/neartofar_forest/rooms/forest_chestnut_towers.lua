-- Room 10651: Neartofar Forest
local Room = {}

Room.id          = 10651
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "Enormous chestnut trees tower above the forest, their broad-rounded crowns one hundred feet in the air.  Massive, wide-spreading branches reach out toward the neighboring trees, providing a safe means of travel for the squirrels that chitter, unseen, from behind a veil of leaves.  Pale green moss covers the ground, its slight phosphorescence the only form of light beneath the canopy of trees."

Room.exits = {
    southwest                = 10650,
    northeast                = 10652,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
