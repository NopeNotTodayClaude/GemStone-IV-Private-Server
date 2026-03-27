-- Room 10727: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10727
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Grey stone, speckled with small patches of soft moss, spreads across the boneyard in a wide swath.  Moonlight washes the rock in a faint white glow.  Few bones lie on the rock, but broken bits of bone line the rock like small bits of gravel.  A large crack streaks through the stone, threatening to break the rock in two."

Room.exits = {
    north                    = 10728,
    south                    = 10726,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
