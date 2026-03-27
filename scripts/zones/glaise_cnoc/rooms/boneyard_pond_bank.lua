-- Room 10724: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10724
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "An eclectic mix of skulls line the bank of the pond.  A pile of various long bones serves as a makeshift stairway out of the pond to the north.  A few lily pads congregate near the bone steps, dark forms against the even darker water."

Room.exits = {
    north                    = 10723,
    southwest                = 10725,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
