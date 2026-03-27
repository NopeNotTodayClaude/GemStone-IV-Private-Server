-- Room 5872: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5872
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "To the north, sunlight bathes an arbor in its warm glow.  Snapdragons in a kaleidoscope of color surround the arbor.  Covered with white clematis, the structure of the arbor is almost completely obscured.  A path of crushed, white marble leads to the arbor."

Room.exits = {
    southeast                = 29576,
    go_arbor                 = 10683,
    go_structure             = 10676,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
