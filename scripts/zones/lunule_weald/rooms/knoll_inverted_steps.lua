-- Room 10553: Lunule Weald, Knoll
local Room = {}

Room.id          = 10553
Room.zone_id     = 8
Room.title       = "Lunule Weald, Knoll"
Room.description = "Several stone steps have been carved into the hillside and would be useful, if they were not inverted.  Large rock formations atop the hill block out the moonlight, deepening the shadows.  A strange whistling sound pierces the silence."

Room.exits = {
    west                     = 10552,
    southwest                = 10554,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
