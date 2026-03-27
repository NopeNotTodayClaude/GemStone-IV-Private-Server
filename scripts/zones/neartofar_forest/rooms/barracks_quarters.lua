-- Room 10671: Neartofar Forest, Barracks
local Room = {}

Room.id          = 10671
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Barracks"
Room.description = "A four-post bed rests atop a pleasant yellow throw rug in one corner of the room, a matching floral comforter only adding to the grotesque effect of finding such furnishings in this location.  Covered with ale cups and papers, a black walnut table leans on one broken leg against a brick wall, surrounded by a variety of armchairs."

Room.exits = {
    east                     = 10668,
    north                    = 10670,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
