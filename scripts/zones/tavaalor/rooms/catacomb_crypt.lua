-- Room 5937: Catacombs, Crypt
local Room = {}

Room.id          = 5937
Room.zone_id     = 2
Room.title       = "Catacombs, Crypt"
Room.description = "Eight masterfully designed sarcophagi fill the chamber.  Entombed within each sarcophagus are the bodies of fallen legends, killed during one or more of the many great wars against different invaders of the city.  Carved to resemble scrolls, the walls above each of the biers served as tombstones with the epitaphs for the slain heroes.  Unfortunately, they are all now very unreadable."

Room.exits = {
    northeast            = 5936,
    southwest            = 5938,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
