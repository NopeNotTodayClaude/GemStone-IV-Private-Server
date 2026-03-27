-- Room 5846: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5846
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path continues to follow the iron fence and the gentle slope of the land makes walking here easy.  Ivy flourishes on the fence, its tendrils almost obscuring the iron pickets.  The stump of an old oak tree provides a home to a family of chipmunks."

Room.exits = {
    southeast                = 5845,
    northwest                = 5847,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
