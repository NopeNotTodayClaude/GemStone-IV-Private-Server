-- Room 3506: Ta'Vaalor, Geaislt Wey
local Room = {}

Room.id          = 3506
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Geaislt Wey"
Room.description = "A low stone wall surrounds a beautiful manor house.  Encircled by luxurious gardens, the manor exudes a comfortable, safe atmosphere.  An ironwood gate marks the entry to the grounds.  Tacked to the gate is a small silver plaque."

Room.exits = {
    north                = 3505,
    southeast            = 3507,
    go_silverwood        = 14659,
}

Room.indoor = false
Room.safe   = true

return Room
