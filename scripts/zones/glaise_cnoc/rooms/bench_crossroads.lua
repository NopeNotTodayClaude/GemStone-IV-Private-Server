-- Room 5882: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5882
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "No graves surround the crossroads, only well-maintained grass.  A wood and iron bench sits in a small field of lush grass.  The iron portion of the bench is painted a glossy black.  The boards forming the seat and back of the bench are meticulously kept clean.  A rose bush grows on either side of the bench.  To the north, the path meanders up a low-rising hill."

Room.exits = {
    north                    = 5890,
    south                    = 5885,
    southeast                = 5881,
    northeast                = 29575,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
