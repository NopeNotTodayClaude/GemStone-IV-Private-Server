-- Room 10692: Catacomb, Chapel
local Room = {}

Room.id          = 10692
Room.zone_id     = 3
Room.title       = "Catacomb, Chapel"
Room.description = "Several long benches face a marble altar on the western wall.  Brass wall sconces support flickering candles, which illuminate this chapel.  Richly embroidered tapestries line the walls with their silken artwork."

Room.exits = {
    east                     = 10685,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
