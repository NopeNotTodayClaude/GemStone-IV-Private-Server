-- Room 31457: Shadowed Forest, Trail
local Room = {}

Room.id          = 31457
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Twisted together in a huge tangle, long deadfalls line the sides of the broken trail.  The trees above close in, enveloping the cleared area in shadows.  Leaves, moss, and bark in various stages of decomposition litter the ground.  Clusters of fungi grow from small nooks in the decaying foliage."

Room.exits = {
    west                     = 31456,
    east                     = 31458,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
