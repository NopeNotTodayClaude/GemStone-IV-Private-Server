-- Room 10615: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10615
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "There are more living trees than dead ones here, as the forest begins to reclaim the village.  A wooden border fence lies fallen over on the ground, no longer serving as protection from the encroaching wildlife.  The songs of a few birds can be heard coming from high in the branches of the living trees.  The contrast of life overtaking death is prominent."

Room.exits = {
    northeast                = 10612,
    north                    = 10613,
    west                     = 10616,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
