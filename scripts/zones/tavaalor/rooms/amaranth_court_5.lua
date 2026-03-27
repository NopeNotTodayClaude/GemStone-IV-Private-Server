-- Room 3492: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3492
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "A deep grey stone cottage sits beside the wey, its doorstep painted a bright green.  Thick glaesine panes mark the window embrasures, each diamond-shaped piece of glaes reflecting and refracting the daylight in a hundred different hues.  A polished haon sign hangs above the door."

Room.exits = {
    east                 = 3489,
    west                 = 3493,
    go_furrier           = 10329,
}

Room.indoor = false
Room.safe   = true

return Room
