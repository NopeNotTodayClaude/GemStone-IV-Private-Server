-- Room 10514: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10514
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "The flapping wings of bats accompanied by their cries, a high-pitched metallic ping, fill the night air.  Mid-sized knolls rise up from the low-lying, sodden ground.  While hopping from one to another makes travel decidedly slower, they do offer some relief from treading through the muddy soil.  The tangle of tree roots, shrubs and plants provide the perfect home for a variety of birds and animals."

Room.exits = {
    north                    = 10513,
    south                    = 10515,
    east                     = 10518,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
