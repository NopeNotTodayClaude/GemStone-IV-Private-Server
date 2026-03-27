-- Room 10382: Ta'Vaalor, Hall of Justice
local Room = {}

Room.id          = 10382
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Hall of Justice"
Room.description = "A thick iron chandelier hangs from the wide-beamed ceiling, casting flickering light across the stone walls and ivory-veined black marble floors of the Hall.  Several plain ironwork sconces line a flight of steps leading upwards into the shadows."

Room.exits = {
    out                  = 3518,
    north                = 3746,
    east                 = 10383,
}

Room.indoor = true
Room.safe   = true

return Room
