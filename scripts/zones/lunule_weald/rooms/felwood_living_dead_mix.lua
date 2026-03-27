-- Room 10563: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10563
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "The forest is crowded with both living and dead trees.  Much of the bark from the dead trees lies on the rotting forest floor, leaving the trunks smooth and dark.  The canopy overhead has thinned slightly, allowing some light to filter into the grove."

Room.exits = {
    southwest                = 10562,
    east                     = 10564,
    south                    = 10575,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
