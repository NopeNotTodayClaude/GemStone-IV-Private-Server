-- Room 10610: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10610
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A small wooden bridge has been built here, though there is no evidence that any water ever flowed beneath it.  The bridge is slightly curved to allow passage underneath, and smooth handrails are available to hold while passing over it.  There appears to be no reason for a bridge to be built in this location, especially one with no floor to walk upon."

Room.exits = {
    northeast                = 10593,
    southeast                = 10595,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
