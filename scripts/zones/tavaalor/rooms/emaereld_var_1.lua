-- Room 3496: Ta'Vaalor, Emaereld Var
local Room = {}

Room.id          = 3496
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Emaereld Var"
Room.description = "A small covered porch wraps around the front of a large shop.  Climbing roses creep up the structure's stone walls, sending cascades of deep red blossoms out into the var.  An elaborate sign hangs from two small hooks on the eaves of the porch."

Room.exits = {
    north                = 3483,
    west                 = 3497,
    go_exchange          = 12348,
}

Room.indoor = false
Room.safe   = true

return Room
