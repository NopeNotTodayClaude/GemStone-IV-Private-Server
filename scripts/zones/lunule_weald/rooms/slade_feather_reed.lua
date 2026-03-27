-- Room 10548: Lunule Weald, Slade
local Room = {}

Room.id          = 10548
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Feather reed grass grows thickly here, hiding a myriad of life and death beneath it.  Pale moonlight barely illuminates the thick grass."

Room.exits = {
    east                     = 10541,
    south                    = 10549,
    southeast                = 10556,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
