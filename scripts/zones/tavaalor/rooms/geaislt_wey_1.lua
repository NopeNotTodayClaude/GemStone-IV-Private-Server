-- Room 3505: Ta'Vaalor, Geaislt Wey
local Room = {}

Room.id          = 3505
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Geaislt Wey"
Room.description = "Well-worn cobblestones fill the street's surface.  A pair of iron posts are topped with iron cutouts shaped like dragons.  The necks of the reptiles droop low to allow for lanterns to hang freely from tiny hooks set into the mouths of the beasts."

Room.exits = {
    northeast            = 3503,
    south                = 3506,
}

Room.indoor = false
Room.safe   = true

return Room
