-- Room 10523: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10523
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "A patch of loose powdery soil produces a low-growing creeping plant that dominates a dead tupelo tree as it twines itself up the length of the trunk.  Moonlight illuminates the surface of the water and reveals an abundance of featherfoils.  Dark pink petals that have fallen from the canes of a swamp rose bush, littering the surface of the water."

Room.exits = {
    northwest                = 10522,
    southeast                = 10524,
    southwest                = 10530,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
