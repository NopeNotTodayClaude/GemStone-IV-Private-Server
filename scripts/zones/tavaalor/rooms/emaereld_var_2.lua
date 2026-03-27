-- Room 3497: Ta'Vaalor, Emaereld Var
local Room = {}

Room.id          = 3497
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Emaereld Var"
Room.description = "The facade of the city's bakery is whimsically painted with a stylized border around the door and wood-framed windows.  The bright red door boasts a handcarved maoral sign.  The air is redolent with the scent of freshly baked bread, cookies, cakes, and other sweet delicacies."

Room.exits = {
    east                 = 3496,
    west                 = 3499,
    south                = 3498,
    go_bakery            = 12349,
}

Room.indoor = false
Room.safe   = true

return Room
