-- Room 10575: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10575
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "The sense of death and decay is pervasive, and not even the sound of crickets chirping disturbs the air.  The damp leaves underfoot make no sound, and the thick canopy above makes the determination of time impossible.  The smell of decay grows stronger, as every step disturbs the rotting leaves and releases their pungent aroma into the stagnant air."

Room.exits = {
    north                    = 10563,
    southwest                = 10573,
    south                    = 10576,
    east                     = 10577,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
