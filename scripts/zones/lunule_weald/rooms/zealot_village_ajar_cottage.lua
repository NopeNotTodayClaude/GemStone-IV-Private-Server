-- Room 10602: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10602
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The front door of this small cottage stands permanently ajar, its rusted hinges bent and deformed.  The outside and roof of the home appear to have remained fairly sturdy, deceptively inviting to weary travelers.  There are no windows to peer inside, the only access being the slightly open door."

Room.exits = {
    east                     = 10598,
    north                    = 10599,
    northwest                = 10601,
    southwest                = 10603,
    northeast                = 10604,
    go_door                  = 10608,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
