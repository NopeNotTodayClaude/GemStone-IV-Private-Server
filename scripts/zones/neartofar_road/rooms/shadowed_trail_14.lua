-- Room 31472: Shadowed Forest, Trail
local Room = {}

Room.id          = 31472
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Thin vines droop from a few of the gigantic and archaic trees that comprise the old forest.  Saplings peek out from piles of moss and other greenery that rule the moist ground.  Curved branches create an arcing canopy above, the thick leaves blanketing the crowns."

Room.exits = {
    west                     = 31471,
    southeast                = 31473,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
