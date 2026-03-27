-- Room 10611: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10611
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The rusting, blackened heads of several yard implements sit in the center of a burned out circle, as if the villagers had inexplicably gathered up their rakes and shovels and burned them.  Ringing the barren soil of the fire circle is a single, continuous row of toadstools."

Room.exits = {
    northwest                = 10597,
    north                    = 10606,
    south                    = 10612,
    southwest                = 10613,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
