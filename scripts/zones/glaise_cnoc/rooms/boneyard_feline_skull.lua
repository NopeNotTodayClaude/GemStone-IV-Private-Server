-- Room 10719: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10719
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Dark green grass fills the area, interrupted frequently by bones half buried in the ground.  A jaw bone rests against a rock, along with other bones from a skeleton.  A skull from some sort of feline lies deep in a clump of tall grass.  Moonlight glints off the moisture that coats the grass."

Room.exits = {
    north                    = 10718,
    southeast                = 10720,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
