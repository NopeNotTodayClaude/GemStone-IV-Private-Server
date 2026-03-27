-- Room 10324: Bank of Ta'Vaalor, Lobby
local Room = {}

Room.id          = 10324
Room.zone_id     = 2
Room.title       = "Bank of Ta'Vaalor, Lobby"
Room.description = "Thick Loenthran carpets in shimmering hues of aubergine, olive and amber cover the smooth stone floors, adding warmth and luxury to the chamber.  A vaulted ceiling, painted with a scene of ancient battle, soars overhead.  Small beams of colored light refracting through the panes of stained glaes windows arc across the otherwise undecorated ivory limestone walls."

Room.exits = {
    out                  = 3488,
    east                 = 10325,
    north                = 10326,
}

Room.indoor = true
Room.safe   = true

return Room
