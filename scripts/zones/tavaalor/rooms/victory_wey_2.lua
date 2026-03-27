-- Room 3517: Ta'Vaalor, Victory Wey
local Room = {}

Room.id          = 3517
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Wey"
Room.description = "Patrons wander into and out of a local inn, some quietly moving on while others congregate and chat amongst themselves.  The thick red roof tiles of the inn glint in the sunlight, brightening the countenance of the inn's pale limestone-clad walls.  Flowerbeds thick with fragrant blossoms flank the inn's blue-painted front door."

Room.exits = {
    west                 = 3516,
    east                 = 3518,
    southeast            = 3543,
    go_malwith           = 10384,
}

Room.indoor = false
Room.safe   = true

return Room
