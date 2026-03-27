-- Room 10677: Glaise Cnoc, Columbarium
local Room = {}

Room.id          = 10677
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Columbarium"
Room.description = "Recessed into the walls are hundreds of niches, each containing urns of cremated remains.  Below each niche small plaques are engraved with the names of those within.  A grey mouse chitters in one corner of the room."

Room.exits = {
    out                      = 5880,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
