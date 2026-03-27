-- Room 3540: Ta'Vaalor, Shimaerslin Wey
local Room = {}

Room.id          = 3540
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimaerslin Wey"
Room.description = "A sturdy wooden gate, carved with fanciful shapes of dragons chasing their tails, stands slightly ajar.  Beds of fragrant blaeston and lavender crowd the wooden fence on either side of the gate.  A shady path leads deeper into the trees."

Room.exits = {
    north                = 3535,
    south                = 3539,
    go_garden            = 10373,
    go_cleric            = 10372,
}

Room.indoor = false
Room.safe   = true

return Room
