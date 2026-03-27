-- Room 5828: Ta'Vaalor, Vermilion Bridge
local Room = {}

Room.id          = 5828
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Vermilion Bridge"
Room.description = "The broad limestone bridge arches gracefully over the Mistydeep River, its pale stone worn smooth by the passage of countless travelers.  Dark water churns swift and cold far below, the current pressing hard against the bridge's ancient pilings.  The Vermilion Gate of Ta'Vaalor rises to the southwest, its ironwork gleaming with dark red enamel and pure gold.  A second span of the bridge continues to the northeast."

Room.exits = {
    northeast                = 5829,
    southwest                = 5827,
    go_gate                  = 3490,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
