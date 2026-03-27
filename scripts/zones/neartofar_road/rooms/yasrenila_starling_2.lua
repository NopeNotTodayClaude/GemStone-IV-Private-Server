-- Room 34460: Yasrenila, Starling Round
local Room = {}

Room.id          = 34460
Room.zone_id     = 5
Room.title       = "Yasrenila, Starling Round"
Room.description = "Bordered by an ivy-wound pentagonal fence on one side and the river on the other, fields stretch out across a section of cleared forest, speckled sparsely with domed structures.  Dorpers doze among the crops beside gathering baskets temporarily abandoned by the farmhands, the forms cast silver in the moonlight.  The flagstone path forks past a glimaergless-paned greenhouse as it winds into the farmland, converting gradually to roads of tamped earth."

Room.exits = {
    southeast                = 34459,
    east                     = 34465,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
