-- Room 10508: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10508
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Stunted white and black mangroves compete with each other for space in this chunk of the swamp.  The cloying fragrance from the black mangrove flowers is almost dizzying.  Overhead, only two or three stars can be seen between the gaps in the trees.  Beehives appear to have been strategically placed on the grey branches to forbid anything foolish enough to try to come near the clusters of white fragrant flowers that grow on the tree."

Room.exits = {
    northwest                = 10506,
    southwest                = 10509,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
