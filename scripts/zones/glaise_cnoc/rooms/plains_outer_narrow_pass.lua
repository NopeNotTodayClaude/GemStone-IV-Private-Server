-- Room 10705: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10705
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "The space between the two walls narrows markedly, forcing many adventurers to scoot through the darkness sideways.  Broken bones lie in small piles in the darkened pass.  To the east, the two walls flare to their widest point."

Room.exits = {
    east                     = 10706,
    west                     = 10704,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
