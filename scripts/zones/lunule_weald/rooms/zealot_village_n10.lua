-- Room 10621: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10621
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Lying in the midst of leaves and forest debris is a large pile of bones.  The bones are humanoid, rotting flesh and cloth still clinging to many of them.  The jumbled pile includes what appear to be full skeletons, though the bones are not attached to each other."

Room.exits = {
    east                     = 10616,
    northwest                = 10620,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
