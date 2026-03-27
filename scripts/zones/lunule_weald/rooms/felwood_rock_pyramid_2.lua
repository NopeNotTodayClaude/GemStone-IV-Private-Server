-- Room 10573: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10573
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "The forest is thick with wide, dark trees.  Silvery moss hangs from nearly every branch, threatening to entangle weary travelers.  A small pyramid of rocks leans against the base of one tree and stuck in the top of the pyramid is a single dead stick."

Room.exits = {
    north                    = 10562,
    south                    = 10574,
    northeast                = 10575,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
