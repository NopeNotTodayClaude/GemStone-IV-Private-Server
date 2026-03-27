-- Room 5829: Timmorain Road, Limestone Bridge
local Room = {}

Room.id          = 5829
Room.zone_id     = 4
Room.title       = "Timmorain Road, Limestone Bridge"
Room.description = "A broad limestone bridge spans the Mistydeep River here, its pale stone worn smooth by years of foot traffic.  The river churns dark and swift below, disappearing beneath the city wall to the southwest where the wall meets the water.  The Vermilion Gate of Ta'Vaalor looms at the bridge's southwestern end, its iron ironwork gleaming with dark red enamel and gold.  To the northeast, a cobblestone road leads into a deciduous forest."

Room.exits = {
    southwest                = 5828,
    go_gate                  = 5828,
    northeast                = 5830,
    go_road                  = 5830,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
