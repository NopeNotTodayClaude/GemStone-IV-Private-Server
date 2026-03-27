-- Room 10578: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10578
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A large dead tree lies upon its side, its rotting branches, leaves and moss litter the forest floor.  Painted and carved into the smooth trunk are letters, symbols and shapes of all sizes.  A small sapling that had struggled to grow from under the dead tree lies trampled in the rotting leaves."

Room.exits = {
    go_tree                  = 10567,
    east                     = 10579,
    southeast                = 10580,
    south                    = 10581,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
