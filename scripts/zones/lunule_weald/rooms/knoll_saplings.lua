-- Room 10546: Lunule Weald, Knoll
local Room = {}

Room.id          = 10546
Room.zone_id     = 8
Room.title       = "Lunule Weald, Knoll"
Room.description = "Several small saplings struggle for purchase in the sloping hillside, the thick grass threatening to overtake them.  The strange whistling sound from atop the hill blends with the light breeze, creating an eerie song."

Room.exits = {
    northeast                = 10545,
    southeast                = 10547,
    southwest                = 10555,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
