-- Room 10745: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10745
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "Here, the top of the stairs begin.  A pair of child-sized skeletons flank the stairway, each with arms raised straight above their heads towards the starry sky.  Even in the strongest wind the two skeletons hold their unusual pose."

Room.exits = {
    northeast                = 10744,
    southeast                = 10746,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
