-- Room 5907: Ta'Vaalor, Victory Gate
local Room = {}

Room.id          = 5907
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Gate"
Room.description = "The towering limestone facade of the Victory Gate is heavily carved with scenes of battle.  Hordes of elves fight faceless wraithen shapes, as flames rise from the ground and jagged, ripped clouds hang above.  Several city guardsmen stand near the gate, inspecting all who pass."

Room.exits = {
    northeast                = 3516,
    southwest                = 5948,
    go_gate                  = 5948,
}

Room.indoor = false
Room.safe   = true

return Room
