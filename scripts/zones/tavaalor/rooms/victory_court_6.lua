-- Room 3541: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3541
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "A large gap in the city wall opens to the southeast, permitting access to the river docks.  City guardsmen patrol the well-fortified wall, ensuring the safety of the city's residents, while customs officials carefully inspect each wagon of cargo hauled from the docks into the city."

Room.exits = {
    northeast            = 3522,
    west                 = 3542,
}

Room.indoor = false
Room.safe   = true

return Room
