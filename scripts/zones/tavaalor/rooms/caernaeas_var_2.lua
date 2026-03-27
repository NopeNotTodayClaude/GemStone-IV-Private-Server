-- Room 3534: Ta'Vaalor, Caernaeas Var
local Room = {}

Room.id          = 3534
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Caernaeas Var"
Room.description = "A small stand of trees crowds up against the high city wall, so thickly gathered that the wall itself is barely visible through the leafy boughs.  A small gate, closed and locked, blocks progress down the lone path that disappears into the deep green bower."

Room.exits = {
    west                 = 3533,
    south                = 3535,
    go_ilynov            = 23541,
}

Room.indoor = false
Room.safe   = true

return Room
