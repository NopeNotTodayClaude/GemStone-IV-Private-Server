-- Room 10374: Ta'Vaalor, Garden of Ancients
local Room = {}

Room.id          = 10374
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Garden of Ancients"
Room.description = "A small niche has been carved into the high city wall, providing a resting place for a small statue of an elven woman.  Thick ferns cluster about the foot of the wall and the bases of the nearby trees.  A small stone bench provides a resting place for quiet contemplation."

Room.exits = {
    north                = 10373,
    south                = 10375,
}

Room.indoor = false
Room.safe   = true

return Room
