-- Room 5850: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5850
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Hidden from view in the foliage of a tall oak tree, the song of several birds fills the air with a melodious trill.  At the base of the oak tree, a simple headstone marks the final resting place of an unknown soul."

Room.exits = {
    northwest                = 5849,
    southwest                = 5851,
    southeast                = 5891,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
