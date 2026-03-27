-- Room 5874: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5874
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A pair of large oak trees flank the gravel path, creating a canopy of leaves overhead.  Sunlight filtering through the leaves creates a mottled pattern on the ground.  Despite the sun, the air remains cool and crisp.  Somewhere nearby, the tranquil voice of a songbird dances in the air."

Room.exits = {
    northeast                = 5875,
    southwest                = 5873,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
