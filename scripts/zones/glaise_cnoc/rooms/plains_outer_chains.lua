-- Room 10695: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10695
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Heavy chains crisscross one another as they pass between the two walls.  The rib cages of various creatures dangle from the chains, swaying slightly with the breeze.  A lone orc skull leans precariously off the top of the inner wall, its jaw open in a soundless scream.  A pair of torches do little to cut through the dark gloom."

Room.exits = {
    east                     = 10696,
    west                     = 10694,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
