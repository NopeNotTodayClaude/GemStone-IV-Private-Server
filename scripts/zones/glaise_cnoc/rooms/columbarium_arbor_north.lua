-- Room 10682: Glaise Cnoc, Columbarium
local Room = {}

Room.id          = 10682
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Columbarium"
Room.description = "Recessed into the walls are hundreds of niches, each containing urns of cremated remains.  Below each niche small plaques are engraved with the names of those within.  At the base of the wall someone has lain a bouquet of fresh flowers."

Room.exits = {
    out                      = 5884,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
