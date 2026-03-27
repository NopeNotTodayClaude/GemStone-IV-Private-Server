-- Room 3531: Ta'Vaalor, Glimaerstone Var
local Room = {}

Room.id          = 3531
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Glimaerstone Var"
Room.description = "The lilting sounds of a flute, emanating from the open windows of a nearby cottage, drift across the var.  Many of the elven passersby smile slightly as they note the bright cadence of the player's tune."

Room.exits = {
    south                = 3530,
    west                 = 3491,
    east                 = 3532,
    go_history           = 10336,
}

Room.indoor = false
Room.safe   = true

return Room
