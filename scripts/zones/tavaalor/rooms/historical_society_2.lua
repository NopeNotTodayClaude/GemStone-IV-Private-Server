-- Room 10337: Ta'Vaalor Historical Society
local Room = {}

Room.id          = 10337
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Historical Society"
Room.description = "White-framed mullioned windows fill the northern wall from floor to ceiling.  The rose garden outside is lushly green, coloring the light that filters into this airy space.  A wicker chaise lounge draped with a fringed silk shawl sits conveniently near a low table laden with iced tea and fresh fruit."

Room.exits = {
    south                = 10336,
    west                 = 10338,
}

Room.indoor = true
Room.safe   = true

return Room
