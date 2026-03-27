-- Room 10326: Bank of Ta'Vaalor, Exchange
local Room = {}

Room.id          = 10326
Room.zone_id     = 2
Room.title       = "Bank of Ta'Vaalor, Exchange"
Room.description = "A rich blue and green Loenthran carpet covers the floor of this small alcove.  A large maoral desk resides in one corner, where the clerk waits to assist patrons with their financial needs.  Piled atop the desk are stacks of blank notes."

Room.exits = {
    out                  = 10324,
}

Room.indoor = true
Room.safe   = true

return Room
