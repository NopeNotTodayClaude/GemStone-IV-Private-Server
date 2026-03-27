-- Room 3527: Ta'Vaalor, Jacinthea Wey
local Room = {}

Room.id          = 3527
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Jacinthea Wey"
Room.description = "A small warehouse sits between the adjacent shops, its stone walls washed a clean white and the door painted a bright blue.  The warehouse's door is bound with a thick ironwood bar clasped by an ironwork hasp and thick padlock."

Room.exits = {
    south                = 3526,
    north                = 3528,
}

Room.indoor = false
Room.safe   = true

return Room
