-- Room 5887: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5887
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The east side of the path is dominated by a marble drake statue at the head of a pair of graves.  A low flame burns constantly in the statue's maw, smoke wafting from the nostrils of the beast.  A simple marble vase adorns each grave.  Fresh white roses fill both vases, while a single blue rose lies at the feet of the statue."

Room.exits = {
    north                    = 5886,
    south                    = 5879,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
