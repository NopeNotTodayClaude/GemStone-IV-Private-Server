-- Room 3483: Ta'Vaalor, Amaranth Wey
local Room = {}

Room.id          = 3483
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Wey"
Room.description = "The crush of passersby makes this busy intersection difficult to navigate.  Above all, the towering gate looms, casting the entire area into deep shadow despite the brightness of day.  A group of guardsmen stands to one side, casually watching the crowd."

Room.exits = {
    east                 = 3484,
    south                = 3496,
    go_gate              = 3727,
}

Room.indoor = false
Room.safe   = true

return Room
