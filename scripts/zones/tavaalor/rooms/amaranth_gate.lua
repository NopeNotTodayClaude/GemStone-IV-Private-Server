-- Room 3727: Ta'Vaalor, Amaranth Gate
local Room = {}

Room.id          = 3727
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Gate"
Room.description = "The towering city gate looms above, its massive edifice built from thick blocks of pale ivory limestone.  Intricate carvings adorn the blocks, each depicting various scenes of battle and occasionally a representation of Koar or Eonak.  City guardsmen flank the gate's opening, inspecting each entrant into the city's vast interior."

Room.exits = {
    southeast                = 3483,
    northwest                = 6103,
    go_gate                  = 6103,
}

Room.indoor = false
Room.safe   = true

return Room
