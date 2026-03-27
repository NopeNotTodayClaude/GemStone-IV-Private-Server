-- Room 10726: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10726
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Bones float in the shallow pond like pale fish while the reflections of stars above twinkle in the water ripples.  In fact, a few fish skeletons can be seen along the low bank.  The bones have been picked clean, no flesh or scales remain."

Room.exits = {
    north                    = 10727,
    northeast                = 10725,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
