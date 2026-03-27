-- Room 10741: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10741
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "A pair of kobold skulls stare blankly out from the hillside into the surrounding night.  The skulls are oddly similar, since they both share a missing socket.  A skeletal, long-fingered hand lies between the skulls."

Room.exits = {
    southwest                = 10740,
    northwest                = 10742,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
