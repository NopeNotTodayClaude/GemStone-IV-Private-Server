-- Room 5848: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5848
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path gently slopes downhill to the northwest as it winds between rows of fragrant lilies.  Growing on both sides of the path, the lilies span the spectrum of color.  Yellow, white and lavender lilies mix with orange, red and multi-colored varieties."

Room.exits = {
    southeast                = 5847,
    northwest                = 5849,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
