-- Room 3493: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3493
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "Teeming with greenery and flowers, the center of the court provides a temporary gathering spot for the residents of the city.  Beds of multicolored peonies, deep green ivy, and the wey's namesake amaranth line the cobblestone square beneath a canopy of thick shade trees.  Sunlight drifts across the cobbles in small patches, moving at the whimsy of the breeze as it stirs the leafy boughs above."

Room.exits = {
    north                = 3486,
    east                 = 3492,
    south                = 3495,
    west                 = 3494,
}

Room.indoor = false
Room.safe   = true

return Room
