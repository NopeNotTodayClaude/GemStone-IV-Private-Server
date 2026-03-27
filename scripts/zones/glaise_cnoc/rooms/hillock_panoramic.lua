-- Room 5847: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5847
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Atop this small hillock a panoramic view of the cemetery spreads out before you.  Despite the crypts, monuments and grave markers, the view before you resembles a vast arboretum.  A profusion of woody plants and carefully cultivated flowers dots the landscape.  Far to the west, sunlight glistens off the Mistydeep River."

Room.exits = {
    southeast                = 5846,
    northwest                = 5848,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
