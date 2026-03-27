-- Room 10634: Neartofar Forest
local Room = {}

Room.id          = 10634
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A faint trail passes through some tall grasses that softly swish in the cool night breeze.  A few soft chirrups signal the presence of night-hunting rodents, which scavenge the grassland for fallen seed.  High overhead, the stars twinkle brightly, only accentuating the dark stillness of the forest."

Room.exits = {
    southwest                = 10625,
    north                    = 10635,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
