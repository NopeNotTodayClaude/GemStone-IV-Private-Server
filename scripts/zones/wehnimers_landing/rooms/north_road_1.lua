-- Room 109: North Road
local Room = {}

Room.id          = 109
Room.zone_id     = 1
Room.title       = "North Road"
Room.description = "A wide cobblestone road stretches north and south through the town.  Tall stone buildings line both sides of the road, their upper floors featuring balconies draped with colorful banners.  The road is well-trafficked with merchants, adventurers, and townspeople."

Room.exits = {
    south     = 101,
    north     = 118,
}

Room.indoor = false
Room.safe   = true

return Room
