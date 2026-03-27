-- Room 10605: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10605
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "A short, rusted fence surrounds the village square.  Flapping in the wind are several bits of material and clothing that have been snagged on the spikes of the old fence.  Around the inside of the border fence are a few stone benches, pitted and crumbling.  Rotting debris and leaves have been blown up against the bottom of the fence, creating homes for insects and other small creatures."

Room.exits = {
    south                    = 10597,
    southwest                = 10604,
    southeast                = 10606,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
