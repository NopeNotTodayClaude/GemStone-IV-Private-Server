-- Room 10338: Ta'Vaalor Historical Society
local Room = {}

Room.id          = 10338
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Historical Society"
Room.description = "The ceiling is much higher here, vaulting up in an uninterrupted expanse of white plaster.  Pride of place is taken by a gilded harpsichord on a low dais.  A scattering of ladder-backed chairs are arranged in casual groupings on the herringbone floor."

Room.exits = {
    east                 = 10337,
    south                = 10339,
}

Room.indoor = true
Room.safe   = true

return Room
