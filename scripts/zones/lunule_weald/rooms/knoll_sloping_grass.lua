-- Room 10552: Lunule Weald, Knoll
local Room = {}

Room.id          = 10552
Room.zone_id     = 8
Room.title       = "Lunule Weald, Knoll"
Room.description = "Sloping slightly, the uneven ground and tall, slick grass make the footing treacherous.  A strange whistling sound can be heard coming from atop the small hill, though nothing can be seen from this distance."

Room.exits = {
    northwest                = 10551,
    east                     = 10553,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
