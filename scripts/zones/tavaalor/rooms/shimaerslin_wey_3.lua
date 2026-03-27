-- Room 3539: Ta'Vaalor, Shimaerslin Wey
local Room = {}

Room.id          = 3539
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimaerslin Wey"
Room.description = "A small but elegant structure stands back from the wey, its outer walls clad in pure white marble.  Twin statues of Koar stand sentinel on either side of the heavily carved front doors.  Standing slightly ajar, the doors provide a glimpse of the cool, dark interior of the building."

Room.exits = {
    north                = 3540,
    south                = 3538,
    go_arkarti           = 10369,
}

Room.indoor = false
Room.safe   = true

return Room
