-- Room 123: East Market Street, Further East
local Room = {}

Room.id          = 123
Room.zone_id     = 1
Room.title       = "East Market Street"
Room.description = "The market continues eastward, the stalls here offering more specialized wares.  An herbalist displays bundles of dried plants, while a jeweler's booth glitters with rings and amulets under a velvet canopy.  The street narrows ahead as it approaches the eastern wall."

Room.exits = {
    west      = 111,
}

Room.indoor = false
Room.safe   = true

return Room
