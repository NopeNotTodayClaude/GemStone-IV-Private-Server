-- Room 5861: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5861
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A unique sculpture resting atop a polished granite base stands in the center of an open glade.  Twin asps curl their long sinuous bodies around the shaft of a tall spear.  Intricately carved feathers, hanging down the sides, adorn the top of the spear.  The sculpture appears to have been carved from a solid piece of silver-veined, black marble."

Room.exits = {
    northwest                = 5860,
    southeast                = 5862,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
