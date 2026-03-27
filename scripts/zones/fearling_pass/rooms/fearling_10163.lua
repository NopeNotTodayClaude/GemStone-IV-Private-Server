-- Room 10163: Fearling Pass, Ravine
local Room = {}
Room.id          = 10163
Room.zone_id     = 9
Room.title       = "Fearling Pass, Ravine"
Room.description = "Between dodging tree trunks and slick rocks, the going is slow here along the bottom of the ravine.  Dappled sunlight gives the area a greenish cast, filtering through the dense canopy far overhead."
Room.exits = {
    southwest                = 10162,
    northeast                = 10164,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
