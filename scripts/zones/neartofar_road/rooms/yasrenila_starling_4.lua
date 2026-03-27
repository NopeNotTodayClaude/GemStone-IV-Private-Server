-- Room 34465: Yasrenila, Starling Round
local Room = {}

Room.id          = 34465
Room.zone_id     = 5
Room.title       = "Yasrenila, Starling Round"
Room.description = "Moonlight catches on the rippled surface of the river as it cascades down low, rocky steps between the high, moss-blanketed banks.  Frogs croak over the murmuring water, hidden in the whispering reeds where fireflies blink in and out of the darkness.  Tucked beneath a round table of stained glass beleria framed in lasimor, latticed chairs provide a front row seat to the aquatic symphony, shadowed by a mixed canopy of foliage."

Room.exits = {
    west                     = 34460,
    east                     = 34461,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
