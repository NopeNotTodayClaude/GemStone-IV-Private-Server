-- Room 18089: Ta'Vaalor, Gem Sales
local Room = {}

Room.id          = 18089
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Gem Sales"
Room.description = "Several velvet-draped tables rest solidly upon a gleaming wooden floor.  Elven guards, strategically placed near them, watch over the tables' precious contents, suspiciously eyeing every patron who enters.  A pair of guards flanks the sole exit, an arched opening leading south."

Room.exits = {
    south                = 10328,
}

Room.indoor = true
Room.safe   = true

return Room
