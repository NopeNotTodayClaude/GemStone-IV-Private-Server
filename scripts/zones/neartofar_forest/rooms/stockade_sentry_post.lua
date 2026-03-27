-- Room 10665: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10665
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "An armor-clad figure slouches against a post in the center of the courtyard, like a derelict sentry on an interminable night watch.  The figure bears a rusting falchion in its drooping right arm, as if it were guarding the stairs leading up to the balcony.  A paper target tacked to the side of the barracks seems to have been used for archery practice."

Room.exits = {
    southeast                = 10660,
    northeast                = 10663,
    up                       = 10666,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
