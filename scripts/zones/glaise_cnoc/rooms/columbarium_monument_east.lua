-- Room 10684: Glaise Cnoc, Columbarium
local Room = {}

Room.id          = 10684
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Columbarium"
Room.description = "Recessed into the walls are hundreds of niches, each containing urns of cremated remains.  Below each niche small plaques are engraved with the names of those within.  In one corner of the room, an old vase holds the dried out remains of various flowers."

Room.exits = {
    out                      = 5875,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
