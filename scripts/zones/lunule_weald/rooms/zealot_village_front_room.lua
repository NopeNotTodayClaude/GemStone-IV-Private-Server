-- Room 10608: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10608
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The inside of this front room has been ravaged by violence.  Every stick of furniture has been hacked to pieces, pillows and cushions ripped to shreds.  The whitewashed walls have been splattered with blood and bits of rotting flesh.  A large knife is imbedded in the wall as if thrown there."

Room.exits = {
    go_door                  = 10602,
    east                     = 10609,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
