-- Room 10606: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10606
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Several large trees have been cut down here and only their stumps remain.  The flat of one stump has a silver crescent moon painted upon it, another has been painted totally black.  Stuck into a hole in the middle of another stump is strange figure made of sticks tied together with thick leather straps.  A light breeze blows through the area, disturbing the leaves and debris on the ground."

Room.exits = {
    north                    = 10595,
    northwest                = 10605,
    south                    = 10611,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
