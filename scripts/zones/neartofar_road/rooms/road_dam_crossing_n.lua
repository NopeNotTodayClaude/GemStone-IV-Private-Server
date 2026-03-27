-- Room 31449: Neartofar Road, Dam
local Room = {}

Room.id          = 31449
Room.zone_id     = 5
Room.title       = "Neartofar Road, Dam"
Room.description = "Wide enough to allow a wagon to pass, the dam's mounded dirt has been packed flat.  Old cobblestones peek from between weeds that have grown over the path.  Grass grows over the downstream side, while fuzzy cattails and golden water lilies crowd the upstream bank.  Water trickles out from the bottom edge of the dam through a cylindrical, dark clay culvert."

Room.exits = {
    north                    = 31448,
    south                    = 31450,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
