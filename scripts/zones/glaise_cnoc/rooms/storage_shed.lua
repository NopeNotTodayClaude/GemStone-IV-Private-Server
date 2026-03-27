-- Room 10675: Glaise Cnoc, Storage Shed
local Room = {}

Room.id          = 10675
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Storage Shed"
Room.description = "Shovels, hoes and rakes hang neatly from pegs on the wall of this old shed.  A small handcart filled with rocks looks as if it has seen recent use.  Broken pieces of an old statue lie in a heap in one corner."

Room.exits = {
    out                      = 5851,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
