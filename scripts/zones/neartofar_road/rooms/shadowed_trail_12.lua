-- Room 31469: Shadowed Forest, Trail
local Room = {}

Room.id          = 31469
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Fallen trees litter the side of the road, their rotting trunks teeming with life as insects and small creatures drift in and out of their wasting forms.  A thin mist hangs in the air, creating a hazy view.  The stale scent of decomposing wood mixes with that of decaying leaves as it floats in the forest air."

Room.exits = {
    northwest                = 31468,
    southeast                = 31470,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
