-- Room 122: Guard Tower, Ground Floor
local Room = {}

Room.id          = 122
Room.zone_id     = 1
Room.title       = "Guard Tower, Ground Floor"
Room.description = "The base of the guard tower is a circular room with thick stone walls.  A spiral staircase winds upward into the tower.  A guard sits at a small desk near the entrance, logging the comings and goings of visitors.  Arrow slits in the walls let in thin beams of light."

Room.exits = {
    out = 106,
    up  = 128,
}

Room.indoor = true
Room.safe   = true

return Room
