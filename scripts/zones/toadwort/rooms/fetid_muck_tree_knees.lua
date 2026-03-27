-- Room 10526: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10526
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "A massive tree dominates the center of an overflowing bourn.  Rising above and scattered throughout the water are the knees of the trees, some of which resemble frogs and other odd shapes.  The eviscerated remains of a large animal lie on the broad surface of one knee.  Dead foliage and fallen branches litter the ground and the smell of long-dead flowers saturates the air.  The soil is a thick, sticky, mixture of mud, rotting flowers and decomposing leaves."

Room.exits = {
    northeast                = 10525,
    northwest                = 10527,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
