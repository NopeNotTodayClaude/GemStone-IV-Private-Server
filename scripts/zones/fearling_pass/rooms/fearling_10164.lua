-- Room 10164: Fearling Pass, Ravine
local Room = {}
Room.id          = 10164
Room.zone_id     = 9
Room.title       = "Fearling Pass, Ravine"
Room.description = "A slight bend in the gully allows the trickling stream to gather into a small pool before it continues over a lip of rock to the northeast.  The pool is still and dark, its surface unbroken except where the stream enters."
Room.exits = {
    southwest                = 10163,
    northeast                = 10165,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
