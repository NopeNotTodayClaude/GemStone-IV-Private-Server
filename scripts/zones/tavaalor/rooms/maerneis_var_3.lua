-- Room 3536: Ta'Vaalor, Maerneis Var
local Room = {}

Room.id          = 3536
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Maerneis Var"
Room.description = "Rose-hued limestone clads an elegant shop set well back from the var.  Beds brimming with foxglove, blaeston, lavender and verbena provide a fragrant carpet upon which bees and butterflies feed with delighted abandon.  An engraved mithril sign is tacked to the doorpost."

Room.exits = {
    west                 = 3525,
    east                 = 3537,
    go_clothier          = 17293,
}

Room.indoor = false
Room.safe   = true

return Room
