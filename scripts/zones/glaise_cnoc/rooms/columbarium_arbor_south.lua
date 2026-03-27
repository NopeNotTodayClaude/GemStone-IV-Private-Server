-- Room 10676: Glaise Cnoc, Columbarium
local Room = {}

Room.id          = 10676
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Columbarium"
Room.description = "Recessed into the walls are hundreds of niches, each containing urns of cremated remains.  Below each niche small plaques are engraved with the names of those within.  Bits of twigs and leaves in one corner of the room are a testament that not everything residing here is dead."

Room.exits = {
    out                      = 5872,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
