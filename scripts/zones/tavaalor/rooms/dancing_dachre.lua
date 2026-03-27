-- Room 10398: Dancing Dahcre, Entry
local Room = {}

Room.id          = 10398
Room.zone_id     = 2
Room.title       = "Dancing Dahcre, Entry"
Room.description = "Gracious and welcoming, this well-appointed foyer is floored in a buttery cream marble, which is subtly veined with smoky grey.  Blue glaesine windows are set into the walls at wide intervals, allowing a small bit of sunlight into the room.  The main source of illumination is an elaborate silver chandelier hanging far above, suspended from the high, arched ceiling."

Room.exits = {
    out                  = 3514,
    east                 = 10399,
    southwest            = 10400,
    south                = 10418,
}

Room.indoor = true
Room.safe   = true

return Room
