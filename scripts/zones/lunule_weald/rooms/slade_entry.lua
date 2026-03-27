-- Room 10540: Lunule Weald, Slade
local Room = {}

Room.id          = 10540
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Tall swamp reeds grow in thick clumps on either side of the muddy trail.  Clouds of insects assail anything that moves here, buzzing loudly and annoyingly.  The occasional croaking of a frog, deep in the reeds, cuts through the perpetual buzzing of the insects.  Darkness provides little relief from the humidity."

Room.exits = {
    up                       = 10539,
    southeast                = 10541,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
