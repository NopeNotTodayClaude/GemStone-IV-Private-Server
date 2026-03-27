-- Room 10673: Glaise Cnoc, Caretaker
local Room = {}

Room.id          = 10673
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Caretaker"
Room.description = "Built into the side of the hillock, this small room has a musty, earthy smell to it, and the air is cool.  An old desk sits in the middle of the room, its drawers securely locked from prying eyes.  On the wall, a map of the cemetery is displayed, in remarkable detail."

Room.exits = {
    out                      = 5835,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
