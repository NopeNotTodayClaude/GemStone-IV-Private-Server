-- Room 3508: Ta'Vaalor, Rubicaene Wey
local Room = {}

Room.id          = 3508
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Rubicaene Wey"
Room.description = "The facade of a guild hall presents an elegant view to the wey.  Clad in white marble flecked with tiny bits of amber, the hall's immense walls are pierced at regular intervals by tall, gleaming glaesine windows.  A brass plaque is affixed to the doorpost."

Room.exits = {
    north                = 3504,
    south                = 3507,
    go_bardguild         = 10438,
}

Room.indoor = false
Room.safe   = true

return Room
