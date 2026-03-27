-- Room 5893: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5893
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A metal sculpture stands tall amid a garden of mournblooms.  The sculpture's patina hides the original finish, but does not diminish its beauty.  The haunting fragrance of the mournblooms fills the air with its sweetness."

Room.exits = {
    south                    = 5869,
    north                    = 24559,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
