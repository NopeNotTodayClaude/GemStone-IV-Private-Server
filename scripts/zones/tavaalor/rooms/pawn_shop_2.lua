-- Room 10380: Ta'Vaalor Antique Goods
local Room = {}

Room.id          = 10380
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Antique Goods"
Room.description = "A polished brass chandelier brightens this cluttered backroom, the flame from its solid white candles reflecting off several antique mirrors hung along the walls.  Narrow aisles wind between teetering crates and velvet-draped tables sorted into a weapon table, an armor table, an arcana table, and a miscellaneous table.  This is where Dakris displays the better bargains and the stranger things recently brought across his counter."

Room.exits = {
    west                 = 10379,
}

Room.indoor = true
Room.safe   = true

return Room
