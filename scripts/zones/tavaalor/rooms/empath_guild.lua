-- Room 10759: Empath Guild, Forecourt
local Room = {}

Room.id          = 10759
Room.zone_id     = 2
Room.title       = "Empath Guild, Forecourt"
Room.description = "A small pocket garden borders a low stone wall running along Gaeld Var, its neatly kept beds showcasing richly colored perennials and fragrant herbs.  Sunshine warmly cavorts about the bright green leaves of the ivy which winds about the beds and along the stone wall.  A brick path bisects the garden leading southerly towards a cloister awash in lush green vines."

Room.exits = {
    out                  = 3510,
    south                = 10760,
}

Room.indoor = true
Room.safe   = true

return Room
