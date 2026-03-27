-- Room 10544: Lunule Weald, Slade
local Room = {}

Room.id          = 10544
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Tall switch grass blows gently in the light breeze.  A few saplings struggle to rise above the grass, stretching upward.  A square piece of leathery skin, snagged on one of the saplings, flaps back and forth in the wind."

Room.exits = {
    east                     = 10543,
    southeast                = 10545,
    west                     = 10558,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
