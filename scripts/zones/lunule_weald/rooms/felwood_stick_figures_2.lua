-- Room 10574: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10574
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "Several stick figures, tied together with a leathery substance, are stuck in the ground at the bases of some of the trees.  Rotting material clings to the figures as if they had been dressed in clothing, and silvery moss resembling hair is attached to the ones with heads."

Room.exits = {
    south                    = 10570,
    north                    = 10573,
    northeast                = 10576,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
