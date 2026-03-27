-- Room 10536: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10536
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Under a cloudless night sky, a small clearing is visible between some trees.  In the center of the clearing, a circle of stones is filled with charred twigs and leaves.  A makeshift hammock is stretched between two tree trunks and is held in place by some of the cord-like vines."

Room.exits = {
    south                    = 10535,
    southeast                = 10537,
    southwest                = 10539,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
