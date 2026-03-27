-- Room 10519: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10519
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "In this section of the swamp, the malodorous fragrance grows increasingly stronger.  Lofty, yellow grass with bearded heads bows slightly under a strong gust of foul wind, sending tiny grains sailing through the air.  Shadows flicker across a ramshackle little shed as the breeze stirs the branches of deformed trees, which surround it.  A pile of bones that are slowly turning to dust rests beside a deep pit that is a few steps away from the shed."

Room.exits = {
    southwest                = 10518,
    northeast                = 10520,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
