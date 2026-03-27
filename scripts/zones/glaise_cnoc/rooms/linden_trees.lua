-- Room 5881: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5881
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Several linden trees line the path, the thick foliage overhead keeping the area cool and shaded.  The small stand of trees is deceptively tranquil.  A red squirrel sits perched in the tree, gnawing on a branch to sharpen its teeth.  The squirrel pauses, as though listening, then continues its gnawing."

Room.exits = {
    southeast                = 5871,
    northwest                = 5882,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
