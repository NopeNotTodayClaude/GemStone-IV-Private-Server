-- Room 3486: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3486
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "Numerous city dwellers wander to and from the northern section of the court, where the large city hall sprawls nearly to the edge of the cobblestoned wey.  A tall carved obelisk stands sentinel in the center of the wey."

Room.exits = {
    north                = 3487,
    east                 = 3488,
    south                = 3493,
    west                 = 3485,
}

Room.indoor = false
Room.safe   = true

return Room
