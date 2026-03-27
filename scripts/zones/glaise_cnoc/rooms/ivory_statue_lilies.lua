-- Room 5853: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5853
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A meticulously carved ivory statue sits amid a circle of golden lilies.  Sunlight bathes the statue in a warm glow and a cool breeze sets the lilies swaying languidly.  Bumblebees hum as they flitter from flower to flower."

Room.exits = {
    southwest                = 5852,
    northeast                = 5854,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
