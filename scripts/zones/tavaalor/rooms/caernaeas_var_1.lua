-- Room 3533: Ta'Vaalor, Caernaeas Var
local Room = {}

Room.id          = 3533
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Caernaeas Var"
Room.description = "The crowd surges along the var, pushing in opposite directions as some seek to travel further into the city while others attempt to leave.  Several city guardsmen stand casually at one corner of the intersection, watching the traffic as it struggles along.  A well-kept shop stands behind the guardsmen."

Room.exits = {
    west                 = 3530,
    north                = 3532,
    east                 = 3534,
    go_archery           = 10362,
}

Room.indoor = false
Room.safe   = true

return Room
