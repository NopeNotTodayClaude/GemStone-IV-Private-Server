-- Room 3543: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3543
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "The pale blue-grey cobblestones of the court have been worn smooth by the many years of traffic and weather, their rounded edges fitted so tightly together that the joints between them are barely visible.  A tall statue towers above the nearby rooftops just to the east, the figure holding aloft a sword that glints in the light with a silvery shimmer."

Room.exits = {
    east                 = 3542,
    northwest            = 3517,
}

Room.indoor = false
Room.safe   = true

return Room
