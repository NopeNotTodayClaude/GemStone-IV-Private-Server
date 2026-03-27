-- Room 10580: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10580
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "Tormented faces have been carved into the smooth, dark trunks of many of the trees, their mouths open as if screaming.  Hanging high in the branches of the carved trees are various pieces of rotting clothing."

Room.exits = {
    northwest                = 10578,
    north                    = 10579,
    west                     = 10581,
    southwest                = 10583,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
