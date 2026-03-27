-- Room 10545: Lunule Weald, Knoll
local Room = {}

Room.id          = 10545
Room.zone_id     = 8
Room.title       = "Lunule Weald, Knoll"
Room.description = "The top of this small hill is littered with odd-shaped rocks and boulders, many of them very tall.  Carved into each stone are strange symbols and letters that form no words.  A loud, piercing whistle emanates from a flute-like tube carved into the top of a particularly tall rock formation.  Several clapperless bells are tethered to other rocks and swing soundlessly in the constant breeze."

Room.exits = {
    northwest                = 10544,
    southwest                = 10546,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
