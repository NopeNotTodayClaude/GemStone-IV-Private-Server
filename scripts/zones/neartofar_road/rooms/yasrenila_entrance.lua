-- Room 34451: Yasrenila Compound, Entrance
local Room = {}

Room.id          = 34451
Room.zone_id     = 5
Room.title       = "Yasrenila Compound, Entrance"
Room.description = "Age-old oaks, elms, and maples bear umbrageous crowns that extend their lush shelter well beyond the edges of the glade they encircle.  Following the organic border, flowering sweetbriar shrouds a sturdy log fence split by a gated, carved beech arbor, the delicate pink blossoms deceptively hiding hooked prickles."

Room.exits = {
    south                    = 34450,
    go_arbor                 = 34452,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
