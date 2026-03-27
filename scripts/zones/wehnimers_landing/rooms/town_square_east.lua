-- Room 103: Town Square, East
local Room = {}

Room.id          = 103
Room.zone_id     = 1
Room.title       = "Town Square, East"
Room.description = "The eastern side of the square is lined with merchant stalls and small shops.  A colorful awning stretches over the entrance to a general store.  The clang of a blacksmith's hammer echoes from somewhere nearby, and the sweet aroma of baked goods mingles with the scent of leather and metal."

Room.exits = {
    west      = 100,
    north     = 105,
    south     = 107,
    east      = 111,
    go_store  = 121,
}

Room.indoor = false
Room.safe   = true

return Room
