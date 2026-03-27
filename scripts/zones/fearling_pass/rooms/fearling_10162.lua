-- Room 10162: Fearling Pass, Ravine
local Room = {}
Room.id          = 10162
Room.zone_id     = 9
Room.title       = "Fearling Pass, Ravine"
Room.description = "Sharply-inclined sides of dark loamy earth carpeted with creeping vines and thorny bushes skirt the narrow path along the bottom of the ravine.  Moisture seeps through the walls, keeping the air cool and damp.  The trail continues northeast along the ravine floor."
Room.exits = {
    southwest                = 10161,
    northeast                = 10163,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
