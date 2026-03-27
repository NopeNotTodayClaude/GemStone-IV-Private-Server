-- Room 5870: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5870
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path is covered with a carpet of oak leaves from a small stand of trees to the north.  A cool breeze sweeping down from the north picks up the leaves and swirls them about, before letting them settle gracefully to the ground again."

Room.exits = {
    northwest                = 29576,
    southeast                = 5869,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
