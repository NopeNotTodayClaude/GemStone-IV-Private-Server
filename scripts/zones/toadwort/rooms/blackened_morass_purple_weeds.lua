-- Room 10532: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10532
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Purple weeds, which stand tall and sturdy about knee-high to a giantman, blanket the ground.  Swirls of deep green, lance-shaped and serrated leaves, about a foot long themselves, cover thick but hollow purple stems.  Rosy pink, purple and white circular clusters of flowers top the stems.  The purple and cream-colored roots are woody with rough hair-like projections."

Room.exits = {
    up                       = 10531,
    east                     = 10533,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
