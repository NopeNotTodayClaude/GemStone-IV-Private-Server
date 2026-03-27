-- Room 3520: Ta'Vaalor, Victory Wey
local Room = {}

Room.id          = 3520
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Wey"
Room.description = "The turrets and crennelated walls of Guardian Keep tower above the city.  Fashioned of pale ivory stone, the ancestral home of House Vaalor is a deceptively lovely stronghold.  Glittering red and gold pennants flutter atop the crimson tiled rooftops.  Several city guardsmen stand in the center of the wey, blocking any progress into the Keep's inner courtyard."

Room.exits = {
    south                = 3519,
    go_keep              = 10441,
    go_burghal           = 26018,
}

Room.indoor = false
Room.safe   = true

return Room
