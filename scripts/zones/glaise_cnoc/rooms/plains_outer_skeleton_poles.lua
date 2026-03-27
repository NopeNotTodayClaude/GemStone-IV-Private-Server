-- Room 10701: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10701
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A forest of steel poles are planted in the ground here.  Each is the final resting place of some poor humanoid.  Only skeletons mark the place of death for dozens upon dozens of humanoids.  Ancient chains bind the grisly remains to their poles.  A family of birds have built a nest atop the skull of one unfortunate victim.  Gaps in the networks of chains overhead seem to focus shafts of moonlight on the skeletons."

Room.exits = {
    north                    = 10700,
    south                    = 10702,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
