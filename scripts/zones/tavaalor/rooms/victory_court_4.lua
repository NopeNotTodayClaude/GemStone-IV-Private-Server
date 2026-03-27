-- Room 3521: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3521
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "Thick grey stone walls clad a large structure that dominates this part of the court.  Red and gold House Vaalor pennants flutter atop the crenelated walls, adding the only bit of color the building possesses.  A plain faenor sign is posted beside the entrance to the imposing hall."

Room.exits = {
    west                 = 3519,
    east                 = 3522,
    go_entrance          = 17215,
}

Room.indoor = false
Room.safe   = true

return Room
