-- Room 5863: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5863
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The iron fence surrounding the cemetery runs close to the path here.  Ivy, growing unchecked, has covered much of the fence with its long green tendrils.  A cluster of birch trees sways under the weight of several squirrels leaping from branch to branch as they chase each other playfully."

Room.exits = {
    northwest                = 5862,
    southeast                = 5864,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
