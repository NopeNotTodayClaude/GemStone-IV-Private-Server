-- Room 10637: Neartofar Forest
local Room = {}

Room.id          = 10637
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A grove of tall elm trees stands in the center of the forest, the area beneath them cleared of underbrush as if to accentuate the majesty of the trees.  Massively thick trunks support long, sinewy branches that reach out and up as if to contain the entire forest in their embrace.  The trees evoke a sense of the age and power of the ancient woods."

Room.exits = {
    northwest                = 10633,
    south                    = 10636,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
