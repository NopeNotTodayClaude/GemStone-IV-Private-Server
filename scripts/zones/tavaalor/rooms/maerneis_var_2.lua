-- Room 3525: Ta'Vaalor, Maerneis Var
local Room = {}

Room.id          = 3525
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Maerneis Var"
Room.description = "Crowds bustle through the intersection, many of the passersby jostling one another in their haste to reach their destinations.  Several city guardsmen watch the crowd with casual interest."

Room.exits = {
    west                 = 3524,
    north                = 3526,
    east                 = 3536,
    go_barracks          = 27929,
}

Room.indoor = false
Room.safe   = true

return Room
