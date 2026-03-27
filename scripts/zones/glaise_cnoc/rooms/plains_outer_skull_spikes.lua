-- Room 10715: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10715
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "The night breeze blows gently between the stone walls, creating a low whistle as it passes through the eye sockets of skulls impaled on spikes set into the outer wall.  Chiseled into the inner wall are images of the skeletons of creatures in Elanthia.  Each image is meticulously detailed in proportion and positioning."

Room.exits = {
    east                     = 10714,
    west                     = 10694,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
