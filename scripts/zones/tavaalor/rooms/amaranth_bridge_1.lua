-- Room 6103: Ta'Vaalor, Amaranth Bridge
local Room = {}

Room.id          = 6103
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Bridge"
Room.description = "A wide limestone bridge spans the northern reach of the Mistydeep River, its pale stones etched with the flowing script of the Vaalor elves.  The river runs dark and swift below, its surface catching the light in silver flashes.  The Amaranth Gate of Ta'Vaalor anchors the southeastern end of the bridge, its pale ivory facade looming against the sky.  A second span of the bridge continues to the northwest toward the far bank."

Room.exits = {
    southeast                = 3727,
    northwest                = 6104,
    go_gate                  = 3483,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
