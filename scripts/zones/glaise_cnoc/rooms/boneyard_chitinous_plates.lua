-- Room 10721: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10721
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Large chitinous plates, possibly from kiramon, cover this stretch of the boneyard.  The plates interlock to form a patchwork of armor.  A few cracks have spread from larger holes which appear to be severe puncture wounds.  Night winds, cool and crisp, flow across the holes, creating a low whistle."

Room.exits = {
    south                    = 10722,
    northwest                = 10720,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
