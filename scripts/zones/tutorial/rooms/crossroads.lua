-- Room 59002: Tutorial - Crossroads
-- Hub connecting the 5 tutorial scenarios

local Room = {}

Room.id          = 59002
Room.zone_id     = 99
Room.title       = "A Shimmering Crossroads"
Room.description = "The mist clears to reveal a crossroads where five paths converge.  Each path glows with a different faint color — a warm gold to the northeast, a soft blue to the northwest, a deep green to the east, a pale silver to the west, and a faint crimson to the north.  A small stone pedestal stands at the center, engraved with ancient runes."

Room.exits = {
    south     = 59001,
    northeast = 59010,
    northwest = 59020,
    east      = 59030,
    west      = 59040,
    north     = 59050,
}

Room.indoor = false
Room.safe   = true

return Room
