-- Room 34459: Yasrenila, Starling Round
local Room = {}

Room.id          = 34459
Room.zone_id     = 5
Room.title       = "Yasrenila, Starling Round"
Room.description = "Camouflaged beneath vines peppered with open moonflowers, dwellings halo an abundant garden featuring a centerpiece of a lichenous pale rhyolite basin amply veined with citrine.  The bifurcated path splits around this rainbow display as it follows the natural border of the forest surrounding the clearing.  Stained with water damage, some varnished wooden disc chimes hang over the northeasterly trail, stirred into a quiet melody by a gentle breeze rustling through the foliage."

Room.exits = {
    south                    = 34455,
    northwest                = 34460,
    northeast                = 34461,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
