-- Room 10723: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10723
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "To the south some crude bone steps lead down into a small pond, ominously dark in the night.  A pair of short stakes flank the steps, each capped with a humanoid skull.  The skulls rock on the posts as the wind blows, like heads nodding.  A nearby tree spreads its bare limbs partially over the lake."

Room.exits = {
    north                    = 10722,
    south                    = 10724,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
