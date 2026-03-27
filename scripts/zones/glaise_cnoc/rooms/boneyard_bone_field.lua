-- Room 10728: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10728
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Long arm bones have been planted in the ground, giving the impression of a field of growing bone.  The night breeze lazily blows through the area, bringing even more chill to the night's cool temperature.  Skeletal hands cap a few of the arms like ghastly blooms on a grisly plant.  A rolton skull rests across two of the vertical bones."

Room.exits = {
    north                    = 10716,
    south                    = 10727,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
