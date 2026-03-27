-- Room 10495: Ta'Vaalor, Annatto Bridge
local Room = {}

Room.id          = 10495
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Annatto Bridge"
Room.description = "The southeastern bank of the Mistydeep River lies just ahead, where the bridge meets the ancient cobblestone of Neartofar Road.  Two black marble drakes rest on pedestals flanking the road's approach — mirror images of those on the far bank near Ta'Illistim.  The river churns steadily below.  Behind you to the northwest, the bridge leads back toward Ta'Vaalor's Annatto Gate."

Room.exits = {
    northwest                = 10494,
    go_bridge                = 10496,
    southeast                = 10496,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
