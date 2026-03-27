-- Room 34461: Yasrenila, Starling Round
local Room = {}

Room.id          = 34461
Room.zone_id     = 5
Room.title       = "Yasrenila, Starling Round"
Room.description = "Emanating a soft glow in the darkness, gold arathiel dandelions warm the window boxes of a hexagonal wood-crafted structure set betwixt the murmuring river as it wends into the woods and a squat olivewood building attached to an ornamented pergola.  A trio of hand-carved oak mushrooms dappled in grey lichen stands amongst the fragrant verdure in a lush herb garden, the greenery flourishing with wild abandon around lasimor plant markers."

Room.exits = {
    southwest                = 34459,
    go_building              = 34462,
    go_structure             = 34464,
    west                     = 34465,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
