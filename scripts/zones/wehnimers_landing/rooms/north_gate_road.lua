-- Room 115: North Gate Road
local Room = {}

Room.id          = 115
Room.zone_id     = 1
Room.title       = "North Gate Road"
Room.description = "The road widens here as it approaches the northern gate of Wehnimer's Landing.  The tall wooden palisade looms ahead, and through the open gate you can see the road continuing north into the Upper Trollfang forest.  A pair of guards eye passing travelers with practiced scrutiny."

Room.exits = {
    southeast = 106,
    south     = 112,
}

Room.indoor = false
Room.safe   = true

return Room
