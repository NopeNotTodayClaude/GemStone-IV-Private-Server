-- Room 3544: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3544
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "Through an opening in the city's fortifying walls, a large dock extends out over the Mistydeep.  Although the boats anchored at the docks appear to be primarily pleasure crafts, there are a few cargo barges floating further out in the river.  A few elven sailors wander the docks seeing to various maintenance tasks."

Room.exits = {
    north                = 3542,
    go_dock              = 10381,
}

Room.indoor = false
Room.safe   = true

return Room
