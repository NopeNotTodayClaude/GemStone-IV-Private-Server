-- Room 10577: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10577
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "In the midst of a small clearing stands an old, enormous tree, its branches reaching high up into the canopy.  The bark on the trunk of the tree is old and rough.  Staring out of the tree's bark is the shape of an old man's face, its eyes wide, its nose misshapen, and its mouth formed into a perpetual scream."

Room.exits = {
    north                    = 10564,
    east                     = 10566,
    south                    = 10568,
    west                     = 10575,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
