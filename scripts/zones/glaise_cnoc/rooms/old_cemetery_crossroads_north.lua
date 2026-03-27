-- Room 5869: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5869
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Thick green grass blankets the ground on each side of the path.  The path continues to the north and south, as well as branching off to both the northeast and northwest.  As the path meanders south, it rises gradually as it climbs a hillock."

Room.exits = {
    south                    = 5868,
    northwest                = 5870,
    northeast                = 5873,
    north                    = 5893,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
