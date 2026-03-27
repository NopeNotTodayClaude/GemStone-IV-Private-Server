-- Room 10595: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10595
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "There are fewer trees here, though the deadfall is still thick and moist with rot.  The trees that do remain are dark, barkless husks, misshapen and malformed.  Long, crooked limbs reach down to snag passersby and entangle them in their branches."

Room.exits = {
    northeast                = 10594,
    southwest                = 10597,
    south                    = 10606,
    northwest                = 10610,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
