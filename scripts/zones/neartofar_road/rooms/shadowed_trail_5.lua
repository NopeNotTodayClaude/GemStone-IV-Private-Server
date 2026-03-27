-- Room 31461: Shadowed Forest, Trail
local Room = {}

Room.id          = 31461
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Bits of stone and rubble scattered about make travel difficult.  Throughout the dense forest, thick climbing plants grasp the bark of the trees, their surfaces damp from the humid climate.  Pale green moss dotted with fungal growth clusters about the trunks."

Room.exits = {
    west                     = 31460,
    south                    = 31462,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
