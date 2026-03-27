-- Room 31454: Neartofar Road
local Room = {}

Room.id          = 31454
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Rugged and coarse, the road meanders through the thick forest, the surrounding terrain undulating with gentle rises and dips.  Thick patches of brambles grow under dense stands of trees.  A thick canopy of branches and leaves weave together, blocking almost all natural light."

Room.exits = {
    north                    = 31453,
    southeast                = 31455,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
