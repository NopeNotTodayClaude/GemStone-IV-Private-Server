-- Room 10616: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10616
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Several pieces of broken furniture are scattered on the ground, bits of wood and glass are buried in the leaves.  A group of mushrooms thrive in the rotting bottom of a splintered drawer.  The shattered glass of a large mirror reflects the moonlight back into the night.  A light wind swirls around the debris, disturbing the dead leaves."

Room.exits = {
    northeast                = 10613,
    east                     = 10615,
    west                     = 10621,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
