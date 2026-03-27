-- Room 5884: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5884
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "To the south, sunlight bathes an arbor in its warm glow.  Snapdragons in a kaleidoscope of color surround the arbor.  Covered with white clematis, the structure of the arbor is almost completely obscured.  A path of crushed, white marble leads to the arbor."

Room.exits = {
    northeast                = 29574,
    go_arbor                 = 10683,
    go_structure             = 10682,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
