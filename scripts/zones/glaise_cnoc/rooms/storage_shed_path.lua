-- Room 5851: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5851
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path curves around a small shed that has been built along its southern side and continues on to the southeast and southwest.  Just beyond the cemetery's fence, a large stand of stately trees blocks any view to the north."

Room.exits = {
    northwest                = 5850,
    southeast                = 5852,
    go_door                  = 10675,
    go_breach                = 10694,
    go_fence                 = 16750,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
