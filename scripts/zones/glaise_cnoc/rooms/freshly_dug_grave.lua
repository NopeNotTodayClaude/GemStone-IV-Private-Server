-- Room 5864: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5864
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A large rectangular hole in the ground marks a freshly dug grave.  A mound of rich, dark soil alongside the hole waits to be backfilled and the musky smell of the earth fills the air.  A pair of shovels have been driven into the mound of dirt, awaiting completion of their work."

Room.exits = {
    northwest                = 5863,
    southeast                = 5865,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
