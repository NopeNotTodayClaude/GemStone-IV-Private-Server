-- Room 10559: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10559
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "Large, old trees tower over the deadfall of the forest floor.  The canopy of their leaves blocks out any light from above, and the air is still and silent.  Lichen grows thickly on the trunks of the dark trees."

Room.exits = {
    west                     = 10547,
    northeast                = 10560,
    east                     = 10572,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
