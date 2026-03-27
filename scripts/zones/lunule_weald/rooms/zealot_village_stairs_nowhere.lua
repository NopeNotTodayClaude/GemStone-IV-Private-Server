-- Room 10604: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10604
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Three wooden steps leading nowhere rise out of the rotting leaves.  There is no debris of a building here and there appears to be no reason for the steps to be in this particular spot.  Imbedded in the top step is the rusting blade of an axe, dark brown splatters have stained the wood surrounding it."

Room.exits = {
    south                    = 10598,
    north                    = 10600,
    southwest                = 10602,
    northeast                = 10605,
    northwest                = 10617,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
