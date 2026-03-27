-- Room 10716: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10716
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Bones, bones and more bones.  The grass is nearly suffocated under the mass of bones lit by the moonlight.  The remains of a tree lie on top of a bone pile, its spindly form almost blending in with the bones."

Room.exits = {
    north                    = 10717,
    south                    = 10728,
    go_hole                  = 10710,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
