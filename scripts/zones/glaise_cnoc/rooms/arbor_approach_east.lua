-- Room 5889: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5889
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Headstones flank both sides of the gravel path here.  Weatherworn, the headstones in this area are obviously older than those which follow the fence enclosing the cemetery.  The gravel path crunches underfoot, but provides an easy route to follow.  To the west sunlight bathes an arbor in its warm glow."

Room.exits = {
    east                     = 5888,
    go_arbor                 = 10683,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
