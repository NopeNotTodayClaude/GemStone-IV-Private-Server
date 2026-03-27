-- Room 10496: Neartofar Road
local Room = {}

Room.id          = 10496
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "An ancient cobblestone road leads from the Mistydeep off into the steadily thickening forest to the southeast.  Two black marble drakes, their attitude of repose belied by one half-opened eye, rest on either side of a massive limestone bridge that crosses the water in the direction of Ta'Vaalor."

Room.exits = {
    go_bridge                = 10495,
    northwest                = 10495,
    southeast                = 10497,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
