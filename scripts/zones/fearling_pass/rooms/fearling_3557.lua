-- Room 3557: Fearling Pass, Cobbled Road
local Room = {}

Room.id          = 3557
Room.zone_id     = 9
Room.title       = "Fearling Pass, Cobbled Road"
Room.description = "Here at the bank of the Mistydeep River stands a large limestone bridge that arches the flowing dark expanse.  A gatehouse of pale stone marks the near end of the bridge, its arched opening framing the span beyond.  The cobblestone road widens at this approach, smoothed by the passage of trade wagons and soldiers alike.  Northward the road climbs gently into the wold."

Room.exits = {
    southeast                = 6104,
    north                    = 6101,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
