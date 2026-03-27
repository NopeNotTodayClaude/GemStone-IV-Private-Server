-- Room 3519: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3519
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "A small cluster of trees stands near the edge of the court, providing a shady spot and a chance for a brief respite from the bustle of the city.  Several elven guards stand beneath a nearby tree, chatting quietly amongst themselves as they scan the crowded court."

Room.exits = {
    west                 = 3518,
    north                = 3520,
    east                 = 3521,
    south                = 3542,
}

Room.indoor = false
Room.safe   = true

return Room
