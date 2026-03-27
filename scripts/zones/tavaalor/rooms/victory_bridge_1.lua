-- Room 5948: Ta'Vaalor, Victory Bridge
local Room = {}

Room.id          = 5948
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Bridge"
Room.description = "The Victory Bridge spans the southern reach of the Mistydeep River in broad, confident arches of pale limestone.  Battle scenes are carved in low relief along the bridge's inner railing — elven soldiers locked in eternal conflict with shadowy figures.  The Victory Gate of Ta'Vaalor stands tall to the northeast, its carved facade watching over all who pass.  A second span of the bridge extends southwest toward the far bank."

Room.exits = {
    northeast                = 5907,
    southwest                = 3549,
    go_gate                  = 3516,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
