-- Room 5830: Timmorain Road
local Room = {}

Room.id          = 5830
Room.zone_id     = 4
Room.title       = "Timmorain Road"
Room.description = "A vibrant deciduous forest presses toward the waters of the Mistydeep River, leaving scant room for passage between the trees and the riverbank.  Cutting into the forest to the northeast, a well-maintained cobblestone road provides sure footing for travelers wishing to venture that direction, while a massive limestone bridge leads southwest, out over the river's waters toward an impressive city."

Room.exits = {
    go_bridge                = 5829,
    northeast                = 5831,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
