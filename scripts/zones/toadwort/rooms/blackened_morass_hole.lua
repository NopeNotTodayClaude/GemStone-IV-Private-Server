-- Room 10531: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10531
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Mutated and wilted swamp buttercups droop listlessly above shallow water.  Fallen leaves and cypress needles litter the ground, almost unnoticed under the dim light of the moon.  A large hole rests near the flared base of a tree that has been split straight down its middle.  At the entrance of the hole, the shredded remains of what may have once been a cloak are visible."

Room.exits = {
    go_log                   = 10507,
    down                     = 10532,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
