-- Room 3487: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3487
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "The imposing facade of the city's great hall borders the edge of the cobblestone wey, allowing scant purchase for the small bed of flowers at its foot.  Carved at regular intervals along the massive limestone walls of the hall, the crest of House Vaalor is further decorated with deep red and gold enamel.  Each crest shimmers brightly in the daylight."

Room.exits = {
    south                = 3486,
    go_wyvern            = 10313,
}

Room.indoor = false
Room.safe   = true

return Room
