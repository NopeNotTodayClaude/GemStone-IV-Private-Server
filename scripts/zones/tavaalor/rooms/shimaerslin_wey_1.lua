-- Room 3535: Ta'Vaalor, Shimaerslin Wey
local Room = {}

Room.id          = 3535
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimaerslin Wey"
Room.description = "The trees thin somewhat as they surround an elegant stone structure nestled at the foot of the city wall.  Constructed of amber-hued sandstone, the building boasts numerous glaes-paned windows that reflect the deep green of the surrounding foliage.  A small sign is mounted upon the ironwork doorpost."

Room.exits = {
    north                = 3534,
    south                = 3540,
    go_clericguild       = 10376,
    go_resort            = 25192,
}

Room.indoor = false
Room.safe   = true

return Room
