-- Room 10564: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10564
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "High up in one of the trees, secured to the trunk by thick leather straps, is a full humanoid skeleton.  One strap lies tightly across the skeleton's forehead, one across its neck, another across its chest, one across its pelvic area and another across its legs.  One arm of the skeleton has been strapped to a branch as if pointing into the distance.  The skeleton's jaw has fallen off and is lodged in the crook of two branches."

Room.exits = {
    west                     = 10563,
    east                     = 10565,
    south                    = 10577,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
