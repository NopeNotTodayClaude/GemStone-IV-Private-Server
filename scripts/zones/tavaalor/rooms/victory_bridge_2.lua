-- Room 3549: Ta'Vaalor, Victory Bridge
local Room = {}

Room.id          = 3549
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Bridge"
Room.description = "The southern bank of the Mistydeep River lies just ahead to the southwest, where the bridge meets a well-worn road stretching south through open countryside toward Victory Road.  The river below is broad and swift, its current humming against the limestone pilings.  Behind you to the northeast, the first bridge span leads back toward the Victory Gate."

Room.exits = {
    northeast                = 5948,
    southwest                = 5950,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
