-- Room 10683: Glaise Cnoc, Arbor
local Room = {}

Room.id          = 10683
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Arbor"
Room.description = "Moonlight filters through the leaves, casting its glow upon two curved benches that provide a place for quiet contemplation.  Cut from black marble and polished to a high gloss, the surface of the benches is worn with use.  Blanketed with clematis, the subtle fragrance of the creamy white flowers fills the air."

Room.exits = {
    west                     = 5877,  -- west spoke of arbor diamond
    north                    = 5872,
    east                     = 5884,
    south                    = 5889,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
