-- Room 10511: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10511
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Moss-draped cypress trees crowd a tiny island.  Under the glow of the full moon, a capsized and warped dory can be seen near the island.  It is easily held in place, as it rocks gently back and forth in the undercurrent, by one of hundreds of cypress roots.  A family of beavers has made a home for themselves in a dead and fallen tree nearby the rotting remains of the dory."

Room.exits = {
    up                       = 10509,
    east                     = 10512,
    south                    = 10517,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
