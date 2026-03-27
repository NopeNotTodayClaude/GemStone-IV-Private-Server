-- Room 10518: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10518
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "A wicked stench permeates the air and the soil becomes moist and sticky with an unknown blackish substance.  The entire structure of the landscape changes dramatically.  Huge boulders are partially embedded in the soil, and most are completely covered with the same thick, blackish muck that also covers the ground.  It is almost as if the ground itself has birthed the stones.  A skull, a pile of bones and what appear to be teeth lie in a small ditch."

Room.exits = {
    west                     = 10514,
    northeast                = 10519,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
