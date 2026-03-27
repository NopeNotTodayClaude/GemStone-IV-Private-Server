-- Room 3510: Ta'Vaalor, Gaeld Var
local Room = {}

Room.id          = 3510
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Gaeld Var"
Room.description = "A whitewashed wooden fence merges with a low stonework barricade covered with a thick, lush carpet of creeping fig.  Bright purple anemones and fragrant yellow buttercups mingle in the scant space available between the cobbled var and the base of the fence."

Room.exits = {
    west                 = 3509,
    east                 = 3511,
    go_empath            = 10759,
}

Room.indoor = false
Room.safe   = true

return Room
