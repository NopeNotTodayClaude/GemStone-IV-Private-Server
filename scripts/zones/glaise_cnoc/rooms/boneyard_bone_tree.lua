-- Room 10718: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10718
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "A small evergreen stands out among the sea of wavy grass.  Hanging from the tree branches is a wide array of bones.  Leg bones, entire hands and even a skull adorn the tree.  The tree itself resembles a skeleton bathed in moonlight."

Room.exits = {
    north                    = 10717,
    south                    = 10719,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
