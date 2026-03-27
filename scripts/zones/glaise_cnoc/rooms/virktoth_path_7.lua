-- Room 10736: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10736
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "An assortment of bones lie across the steps, some are actually fused with the stairway.  One skull appears to have melted down into the steps, only the eye sockets and above remain whole.  A human thigh bone has been fused with the edge of one of the steps and now stands vertically.  A bank of mist rolls through the night, clinging slightly to the stairway."

Room.exits = {
    southeast                = 10737,
    northwest                = 10735,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
