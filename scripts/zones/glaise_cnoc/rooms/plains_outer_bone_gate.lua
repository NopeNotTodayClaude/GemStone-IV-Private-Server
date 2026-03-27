-- Room 10702: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10702
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "An elaborate gate made of bone is set into the outer wall.  Now sealed by a fused lock, the gate looks out on a short path leading to a now collapsed bridge.  The water quickens through the smaller channel formed by the bridge remains.  Moonlight filters through the gate, casting a shadowy image of the gate on the grey ground."

Room.exits = {
    south                    = 10701,
    northeast                = 10703,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
