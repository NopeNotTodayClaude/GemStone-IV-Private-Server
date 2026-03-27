-- Room 10588: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10588
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "Clumps of rotting moss, still clinging to the upper-most branches of the dead trees, sway continuously in the incessant breeze.  The scream of hawk echoes through the forest, providing an eerie note to the song of the howling wind."

Room.exits = {
    northwest                = 10583,
    southeast                = 10589,
    west                     = 10591,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
