-- Room 10158: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10158
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "The incline becomes a bit more challenging as the trail turns slightly and approaches the boundaries of the forest ahead.  Outcroppings of dark granite jut through the thin soil on either side, and roots from nearby trees snake across the path."
Room.exits = {
    southwest                = 10122,
    north                    = 10159,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
