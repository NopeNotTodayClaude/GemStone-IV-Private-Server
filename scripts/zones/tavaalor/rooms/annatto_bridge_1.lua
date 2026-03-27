-- Room 10494: Ta'Vaalor, Annatto Bridge
local Room = {}

Room.id          = 10494
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Annatto Bridge"
Room.description = "The Annatto Bridge crosses the eastern fork of the Mistydeep River in long, graceful arches of pale limestone.  Stylized vines and flowers matching those carved on the Annatto Gate are repeated here along the bridge's low railing, worn smooth by countless hands.  The gate itself anchors the northwestern end of the bridge.  A second span continues southeast toward the far bank and the Neartofar road beyond."

Room.exits = {
    northwest                = 5906,
    southeast                = 10495,
    go_gate                  = 3523,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
