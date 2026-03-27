-- Room 10600: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10600
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "In the center of the village square is a crumbling stone fountain.  It is difficult to tell the original shape of the sculpture in the fountain and it appears to have been deliberately destroyed.  Several heavy, rusted sledgehammers and pick-axes are scattered within the stone debris."

Room.exits = {
    southeast                = 10597,
    southwest                = 10599,
    south                    = 10604,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
