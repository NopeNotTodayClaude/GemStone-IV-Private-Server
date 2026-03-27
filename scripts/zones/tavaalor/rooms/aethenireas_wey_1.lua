-- Room 3501: Ta'Vaalor, Aethenireas Wey
local Room = {}

Room.id          = 3501
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Aethenireas Wey"
Room.description = "Tall privet hedges guard the front of several small buildings.  The hedges part for small stone steps that lead to barred doors.  A single glaes-paned mithglin lantern hangs above each door."

Room.exits = {
    north                = 3498,
    south                = 3514,
    go_stockade          = 10419,
}

Room.indoor = false
Room.safe   = true

return Room
