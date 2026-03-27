-- Room 10549: Lunule Weald, Slade
local Room = {}

Room.id          = 10549
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "A small pyramid of piled rocks sits alone in the thick grass.  Some of the rocks are painted black and some silver.  Stuck into the top of the rock pile is a moss-covered stick.  The ground is moist and spongy, the air thick and humid."

Room.exits = {
    north                    = 10548,
    south                    = 10550,
    east                     = 10556,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
