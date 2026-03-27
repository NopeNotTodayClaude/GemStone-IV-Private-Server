-- Room 5860: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5860
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A small natural spring bubbles up from a cluster of rocks and cascades into a reflecting pool.  Ripples from the flowing water slowly spread out from the center of the pool in ever-widening circles.  Several large red and white fish swim lazily along the edge of the pool."

Room.exits = {
    north                    = 5859,
    southeast                = 5861,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
