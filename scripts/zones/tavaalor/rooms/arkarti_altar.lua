-- Room 10370: Hall of the Arkati, Altar
local Room = {}

Room.id          = 10370
Room.zone_id     = 2
Room.title       = "Hall of the Arkati, Altar"
Room.description = "Golden light filters into the chamber from a diamond-paned glaesine skylight high above.  Raw silk carpets cover the floor and the pale undecorated walls have the smooth ivory gleam of aged lime plaster.  A carved haon altar sits upon a small dais.  Atop the altar, a lone white candle burns steadily."

Room.exits = {
    east                 = 10369,
}

Room.indoor = true
Room.safe   = true

return Room
