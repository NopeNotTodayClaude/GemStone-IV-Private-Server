-- Room 26025: Burghal Enclave, Caernaeas Var
local Room = {}

Room.id          = 26025
Room.zone_id     = 2
Room.title       = "Burghal Enclave, Caernaeas Var"
Room.description = "A streak of unmined vaalorn runs through the tunnel wall, making a long line of dusky cornflower that stands out sharply against a matrix of white tufa.  The brick arches that periodically support the ceiling are carefully arranged to avoid obscuring any of the metallic inclusion.  Past the last of the arches, the tunnel truncates at a large, metal-banded door."

Room.exits = {
    west                 = 26024,
}

Room.indoor = true
Room.safe   = true

return Room
