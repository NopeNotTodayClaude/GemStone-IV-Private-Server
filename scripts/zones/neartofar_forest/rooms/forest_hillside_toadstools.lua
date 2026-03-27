-- Room 10644: Neartofar Forest, Hillside
local Room = {}

Room.id          = 10644
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Hillside"
Room.description = "Some luminescent toadstools grow in the darkness beneath the stockade wall, their faint glow adding to the silvery moonlight that bathes the clearing with an unwholesome glow.  Not far from the mushrooms, several abandoned buckets and barrels sit in a haphazard pile, many having spilled their contents through holes in their wooden staves.  A long pole hangs out over the eastern wall of the stockade, a block and tack attached to its end."

Room.exits = {
    southwest                = 10643,
    east                     = 10645,
    northwest                = 10656,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
