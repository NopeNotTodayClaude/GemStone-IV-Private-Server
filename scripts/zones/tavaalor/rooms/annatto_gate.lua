-- Room 5906: Ta'Vaalor, Annatto Gate
local Room = {}

Room.id          = 5906
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Annatto Gate"
Room.description = "Tremendous white limestone blocks form the massive edifice that is the Annatto Gate.  Stylized vines and flowers are carved along the stones surrounding the arched opening."

Room.exits = {
    northwest                = 3523,
    southeast                = 10494,
    go_gate                  = 10494,
}

Room.indoor = false
Room.safe   = true

return Room
