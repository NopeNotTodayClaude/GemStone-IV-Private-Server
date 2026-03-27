-- Room 10541: Lunule Weald, Slade
local Room = {}

Room.id          = 10541
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "A thick carpet of emerald-green moss covers the spongy ground.  The incessant buzz of insects and the burbling of the pervasive mud create an eerie music echoing through the area.  The air is humid and still."

Room.exits = {
    northwest                = 10540,
    southeast                = 10542,
    west                     = 10548,
    southwest                = 10556,
    south                    = 10557,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
