-- Room 10576: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10576
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "A large blackened tree has been split down the middle and killed.  Growing in the center of the split trunk is a large group of mushrooms, their caps and stalks crawling with worms and insects.  The base of the tree is surrounded with dead bark, moss and leaves in various stages of decomposition."

Room.exits = {
    east                     = 10568,
    southeast                = 10569,
    southwest                = 10574,
    north                    = 10575,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
