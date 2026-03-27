-- Room 10733: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10733
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The stair continues to curve as it ascends to the southwest.  Lengths of rusted chain dangle from the railing like a curtain of iron.  Flecks of rust swirl away from the chains with the night breeze."

Room.exits = {
    northeast                = 10732,
    southwest                = 10734,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
