-- Room 3499: Ta'Vaalor, Emaereld Var
local Room = {}

Room.id          = 3499
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Emaereld Var"
Room.description = "Lanterns swing from lamppost situated at the corner of the var, their glaesine-paned windows glimmering in the sunlight.  Townsfolk hurry along the var, intent upon their business of the hour."

Room.exits = {
    east                 = 3497,
    south                = 3500,
    go_bastion           = 24511,
}

Room.indoor = false
Room.safe   = true

return Room
