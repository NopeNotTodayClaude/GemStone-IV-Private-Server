-- Room 31445: Neartofar Road
local Room = {}

Room.id          = 31445
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Tree cover spreads out above the road, the gravel dappled by spots of sunlight shining through the leaves.  Partially cleared, large branches of deadfall remain at the sides.  Small holes and paths give evidence that various small creatures have found passage through."

Room.exits = {
    northwest                = 31444,
    southeast                = 31446,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
