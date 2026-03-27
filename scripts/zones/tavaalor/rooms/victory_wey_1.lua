-- Room 3516: Ta'Vaalor, Victory Wey
local Room = {}

Room.id          = 3516
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Wey"
Room.description = "A large stone-clad building sits back from the cobbled wey, its doors and windows thrown open.  The clanging sound of hammer on metal rings through the area as smiths do their part to keep the city well armed.  A small bronze plaque hangs upon the doorpost.  A stone walkway snakes around to the rear of the building."

Room.exits = {
    north                = 3515,
    east                 = 3517,
    go_gate              = 5907,
    go_armory            = 12350,
    go_walkway       = 10394,
    go_battlements       = 25587,
}

Room.indoor = false
Room.safe   = true

return Room
