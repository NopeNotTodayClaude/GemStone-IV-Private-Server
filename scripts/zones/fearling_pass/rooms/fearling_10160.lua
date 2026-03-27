-- Room 10160: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10160
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "The brush and other undergrowth here is quite dense as the pass dodges around outcroppings of lichen-covered granite and hunched, wind-shaped trees.  Birdsong echoes from somewhere deep in the thicket to the east."
Room.exits = {
    south                    = 10159,
    north                    = 10161,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
