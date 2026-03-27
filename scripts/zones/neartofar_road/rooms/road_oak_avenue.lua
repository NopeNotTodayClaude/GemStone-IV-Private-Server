-- Room 10497: Neartofar Road
local Room = {}

Room.id          = 10497
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Raised above the level of the underbrush and banked to provide for drainage after storms, the road provides a safe and comfortable journey through the forest.  Constant maintenance keeps the road clear of leaves and twigs, and the acorns that pose an even more serious danger to the cobblestone pavement.  At either side of the road, small clumps of young oaks grow out of refuse piles left by the road-clearing crews."

Room.exits = {
    northwest                = 10496,
    southeast                = 10498,
    climb_bank               = 10499,
    go_oaks                  = 10622,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
