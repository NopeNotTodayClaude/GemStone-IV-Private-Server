-- Room 5859: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5859
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path winds its way around a small mausoleum as it climbs the gentle slope of the knoll.  Carefully pruned boxwoods grow along both sides and the back of the small building.  Far to the west, sunlight glints off the waters of the Mistydeep River."

Room.exits = {
    north                    = 5858,
    south                    = 5860,
    go_door                  = 10679,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
