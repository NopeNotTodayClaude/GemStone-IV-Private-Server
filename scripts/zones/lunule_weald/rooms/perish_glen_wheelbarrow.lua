-- Room 10591: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10591
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "The remains of a wheelbarrow is partially buried in the ground, dead leaves and other debris are piled up against it.  Spilling out of the rotting wheelbarrow and partially buried in the soil are several bleached bones."

Room.exits = {
    northwest                = 10582,
    northeast                = 10583,
    east                     = 10588,
    southwest                = 10592,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
