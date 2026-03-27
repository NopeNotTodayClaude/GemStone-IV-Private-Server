-- Room 10712: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10712
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A giantman skeleton hangs from the outer wall, still in the shackles that held its living form.  Several of the ribs show deep gouges while the breast bone is cracked severely.  Darkness obscures some of the more gruesome aspects of the skeleton.  The skull lies shattered at the feet of the grisly sight."

Room.exits = {
    north                    = 10711,
    southwest                = 10713,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
