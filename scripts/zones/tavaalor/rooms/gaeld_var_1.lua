-- Room 3509: Ta'Vaalor, Gaeld Var
local Room = {}

Room.id          = 3509
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Gaeld Var"
Room.description = "Several small homes border the var, each finely crafted from grey stone and trimmed with copper guttering.  Elaborate steps lead to the front doors, each seemingly carved from large blocks of wood.  Lanterns are set above some of the doors while simple candle sconces adorn others."

Room.exits = {
    north                = 3507,
    east                 = 3510,
    go_forge             = 17805,
}

Room.indoor = false
Room.safe   = true

return Room
