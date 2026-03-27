-- Room 5839: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5839
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Lush grass carpets the ground on either side of the path that continues to follow the iron fence.  A climbing rosebush completely obscures a large section of the fence behind a profusion of buds, thorns and leaves."

Room.exits = {
    southwest                = 5838,
    northeast                = 5840,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
