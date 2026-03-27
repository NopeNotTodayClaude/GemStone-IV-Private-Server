-- Room 3528: Ta'Vaalor, Jacinthea Wey
local Room = {}

Room.id          = 3528
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Jacinthea Wey"
Room.description = "Rose-hued sandstone clads the facade of an elegant shop, the blocks fitted so tightly together that the seams are nearly invisible.  Cascades of pale pink roses drift in fragrant clouds from a trellis surrounding the shop's front door.  A small silver sign is tacked to the doorpost."

Room.exits = {
    south                = 3527,
    north                = 3529,
    go_clothier          = 17292,
}

Room.indoor = false
Room.safe   = true

return Room
