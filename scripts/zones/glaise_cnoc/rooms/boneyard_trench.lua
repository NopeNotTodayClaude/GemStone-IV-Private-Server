-- Room 10717: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10717
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "A small trench cuts through the grass and bones.  Muddy water, black in the night darkness, flows through the small stream, occasionally dislodging a small bone to send it downstream.  An enormous leg bone from an unknown creature rests in the stream, diverting it into two small channels."

Room.exits = {
    north                    = 10716,
    south                    = 10718,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
