-- Room 3511: Ta'Vaalor, Gaeld Var
local Room = {}

Room.id          = 3511
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Gaeld Var"
Room.description = "A pair of high walls flank the street here, and are capped with stone planters, now home to several species of ferns.  Some of the mortar holding the walls together has crumbled, sending cracks through many of the bricks."

Room.exits = {
    west                 = 3510,
    north                = 3512,
    east                 = 3515,
    go_dye               = 13547,
}

Room.indoor = false
Room.safe   = true

return Room
