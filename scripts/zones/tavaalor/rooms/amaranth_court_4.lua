-- Room 3488: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3488
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "Towering high above, the stone facade of the city's bank presents a windowless face to the cobbled wey.  Twin ironwork doors are flanked by city guardsmen who impassively watch every patron that comes and goes from within the building's darkened interior.  A large mithril plaque is mounted to the stone walls beside the front doors."

Room.exits = {
    west                 = 3486,
    southeast            = 3489,
    go_bank              = 10324,
}

Room.indoor = false
Room.safe   = true

return Room
