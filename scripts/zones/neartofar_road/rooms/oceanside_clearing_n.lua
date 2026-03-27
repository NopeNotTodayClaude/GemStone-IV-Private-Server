-- Room 31473: Oceanside Forest, Clearing
local Room = {}

Room.id          = 31473
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Clearing"
Room.description = "Few trees grow in the small clearing, allowing the warm sunlight to shine down on the plants below.  Clumps of golden curry plants and dark blue cornflowers climb above the greenery on the side of the road.  Bits of cobblestone give way to a pebbled surface, the loose pale stones marbled with grey."

Room.exits = {
    northwest                = 31472,
    southeast                = 31474,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
