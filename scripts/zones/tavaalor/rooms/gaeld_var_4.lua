-- Room 3515: Ta'Vaalor, Gaeld Var
local Room = {}

Room.id          = 3515
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Gaeld Var"
Room.description = "Graceful limestone columns flank the delicate glaesine windows of a nearby shop.  Thick bougainvillea trails from the walls and roof, casting wafting clouds of pink and lavender blossoms across the wey.  A small silver sign is tacked to the establishment's front door."

Room.exits = {
    west                 = 3511,
    south                = 3516,
    go_barracks          = 25583,
}

Room.indoor = false
Room.safe   = true

return Room
