-- Room 3500: Ta'Vaalor, Shimeraern Var
local Room = {}

Room.id          = 3500
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimeraern Var"
Room.description = "A small but elegant building sits beside the var, its crimson-hued tile roof gleaming in the light.  Numerous well-dressed elven patrons wander about the premises.  An ebonwood sign is displayed in one of the large front windows."

Room.exits = {
    north                = 3499,
    east                 = 3498,
    west                 = 3502,
    go_mess              = 25585,
}

Room.indoor = false
Room.safe   = true

return Room
