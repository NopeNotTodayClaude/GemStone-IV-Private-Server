-- Room 10339: Ta'Vaalor Historical Society
local Room = {}

Room.id          = 10339
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Historical Society"
Room.description = "A maze of overstuffed armchairs and delicate end tables makes navigation through this room a tricky proposition.  Heavy celadon velvet drapes cover the windows and pool on the dark floor beneath.  Displayed atop the red marble fireplace is a collection of glass plates filled with bright pinwheels of color."

Room.exits = {
    north                = 10338,
    east                 = 10336,
}

Room.indoor = true
Room.safe   = true

return Room
