-- Room 5837: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5837
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The cemetery path, almost gardenlike in appearance, continues on through land carefully cultivated with trees, shrubs and flowers.  To the southeast honeysuckle decorates the iron fence enclosing the cemetery, its scarlet trumpets filling the air with a sweet fragrance."

Room.exits = {
    southwest                = 5836,
    northeast                = 5838,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
