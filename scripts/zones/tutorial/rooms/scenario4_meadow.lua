-- Room 59042: Scenario 4 - Herb meadow for foraging
local Room = {}

Room.id          = 59042
Room.zone_id     = 99
Room.title       = "A Meadow of Wildflowers"
Room.description = "A lush meadow stretches before you, thick with wildflowers and herbs.  The air is fragrant with the scent of healing plants.  You spot clusters of green moss near a fallen log, and sprigs of white herb growing in the shade of a boulder."

Room.exits = {
    south = 59040,
}

Room.indoor = false
Room.safe   = true

return Room
