-- Room 31448: Neartofar Road, Dam
local Room = {}

Room.id          = 31448
Room.zone_id     = 5
Room.title       = "Neartofar Road, Dam"
Room.description = "Dotted with low-branching pear trees, a sunny meadow flanks the cobbled road, its grass teasing at the stone edges with wild overgrowth.  The southern edge of the grassy field highlights a bright thread of silvery stream held back into a small pond by a wide earthen dam that serves as a pathway across."

Room.exits = {
    north                    = 31447,
    go_dam                   = 31449,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
