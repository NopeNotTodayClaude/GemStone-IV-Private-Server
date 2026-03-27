-- Room 31463: Shadowed Forest, Trail
local Room = {}

Room.id          = 31463
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Far-reaching and dense, the forest spans out in all directions, quickly lost in the darkness.  Curving branches create an enclosed natural archway blocking all but the thinnest rays of light.  Ruts and bumps mar the debris-covered cobblestone road, the way outlined by thick walls of entwined brush on either side."

Room.exits = {
    north                    = 31462,
    east                     = 31464,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
