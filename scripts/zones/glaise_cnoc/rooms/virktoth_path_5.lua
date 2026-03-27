-- Room 10734: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10734
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The steps seem to go on endlessly, seemingly trying to touch the dark heavens in a slow ascent.  The bone railing ends, no longer a safety net for the careless traveller.  A thin covering of the fine grey dirt rests on the steps in large patches."

Room.exits = {
    northeast                = 10733,
    southwest                = 10735,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
