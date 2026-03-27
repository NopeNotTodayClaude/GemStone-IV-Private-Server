-- Room 5856: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5856
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Ankle-high grass sways in the breeze, rippling across the field.  A lone bronze marker, almost hidden by the grass, glints in the sunlight.  Small bunches of wild violets dot the field with color."

Room.exits = {
    southwest                = 5855,
    northeast                = 5857,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
