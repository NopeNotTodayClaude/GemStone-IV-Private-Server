-- Room 10581: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10581
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A myriad of insects have made their homes in the rotting bark surrounding the bases of the tall, dead trees.  Insect holes mar the smooth, dark trunks and spider webs sparkle in the sunlight.  Rotting moss hangs low on the remaining dead branches."

Room.exits = {
    north                    = 10578,
    northeast                = 10579,
    east                     = 10580,
    southwest                = 10582,
    southeast                = 10583,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
