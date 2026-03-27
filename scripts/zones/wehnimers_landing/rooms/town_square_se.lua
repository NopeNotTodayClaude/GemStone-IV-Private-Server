-- Room 107: Town Square, Southeast
local Room = {}

Room.id          = 107
Room.zone_id     = 1
Room.title       = "Town Square, Southeast"
Room.description = "The southeastern corner of the square opens toward the harbor district.  The masts of sailing vessels peek above the rooftops to the south.  A small wooden booth manned by a grizzled old sailor displays maps and navigation charts."

Room.exits = {
    northwest = 100,
    north     = 103,
    west      = 102,
    southeast = 116,
}

Room.indoor = false
Room.safe   = true

return Room
