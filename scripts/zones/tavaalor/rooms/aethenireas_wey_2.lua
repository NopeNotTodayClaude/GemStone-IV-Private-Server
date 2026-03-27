-- Room 3514: Ta'Vaalor, Aethenireas Wey
local Room = {}

Room.id          = 3514
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Aethenireas Wey"
Room.description = "A long, single story building stretches out in the shadow of the Keep.  Constructed of nearly-white limestone, the structure is pierced at regular intervals by pale blue glaesine windows.  Beds thick with begonias, anemones, and ivy nestled beneath neatly trimmed hedges surround the building.  An engraved faenor sign is mounted next to the front door."

Room.exits = {
    north                = 3501,
    south                = 3513,
    go_dancing_dachre    = 10398,
}

Room.indoor = false
Room.safe   = true

return Room
