-- Room 3522: Ta'Vaalor, Annatto Wey
local Room = {}

Room.id          = 3522
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Annatto Wey"
Room.description = "A squat but well-kept stone structure rests in the deep shade of the towering Annatto Gate.  The thick stone walls, capped by a rather flat red tile roof, are pierced by a single bright crimson door.  A small maoral sign is tacked to the doorpost."

Room.exits = {
    west                 = 3521,
    east                 = 3523,
    southwest            = 3541,
    go_antique           = 10379,
}

Room.indoor = false
Room.safe   = true

return Room
