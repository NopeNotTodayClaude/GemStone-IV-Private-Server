-- Room 10594: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10594
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A single, huge tree stands in the midst of this small clearing.  Its trunk is wide and thick, its dead branches still reaching for the sky.  Hundreds of tiny, colorful crescent moons are tied to every limb and branch in this tall tree, creating the effect of a rainbow of leaves swaying in the wind.  At the base of the tree, partially covered with debris, is a small hole."

Room.exits = {
    northeast                = 10590,
    northwest                = 10593,
    southwest                = 10595,
    go_hole                  = 10596,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
