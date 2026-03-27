-- Room 10653: Neartofar Forest
local Room = {}

Room.id          = 10653
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail bends to the southeast and southwest, curving around the base of a hill that rises to the south.  A third track heads in that direction, beginning a climb that ends at a wooden structure perched atop the hill.  By some strange coincidence, a parliament of owls has convened on the limbs of a single red maple at the convergence of the trails."

Room.exits = {
    southwest                = 10652,
    southeast                = 10654,
    south                    = 10656,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
