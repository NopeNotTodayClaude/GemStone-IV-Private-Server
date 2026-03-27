-- Room 31470: Shadowed Forest, Trail
local Room = {}

Room.id          = 31470
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Dipping down a small embankment, the road turns into a stagnant pool of filmy water.  Tiny water bugs flit across the surface, managing to move about the layer of grime gracefully.  Damp leaves cushion the roadway, giving some traction over an underlayer of mud."

Room.exits = {
    northwest                = 31469,
    east                     = 31471,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
