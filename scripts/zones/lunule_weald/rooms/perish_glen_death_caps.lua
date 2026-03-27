-- Room 10586: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10586
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "The stark white of the death cap mushrooms growing atop a tangle of fallen branches and decaying leaves contrasts with the darkness of the rotting forest debris.  Several limbs and branches have split and nearly broken from their dead trunks, their ends pointing into the rotting soil."

Room.exits = {
    north                    = 10585,
    northwest                = 10587,
    east                     = 10592,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
