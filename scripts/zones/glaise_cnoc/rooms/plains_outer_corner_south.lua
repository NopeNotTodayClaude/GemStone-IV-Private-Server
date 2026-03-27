-- Room 10707: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10707
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "The walls turn the path sharply to the southeast.  The bones of small varmints crunch underfoot with each step.  Nearby, a section of the outer wall has collapsed into the darkness of the night.  The rubble prevents any passage through the portal, however."

Room.exits = {
    west                     = 10706,
    southeast                = 10708,
    go_path                  = 10729,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
