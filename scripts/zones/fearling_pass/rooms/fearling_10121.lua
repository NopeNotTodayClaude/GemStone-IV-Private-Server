-- Room 10121: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10121
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "Dirt pebbled with rounded stones forms this pass that concludes at the bank of a lake to the north.  A short dock juts out over the dark water, its weathered planks green with algae.  The trail continues south toward the cobblestone road."
Room.exits = {
    southwest                = 10270,
    north                    = 10122,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
