-- Room 3526: Ta'Vaalor, Jacinthea Wey
local Room = {}

Room.id          = 3526
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Jacinthea Wey"
Room.description = "The amber-colored limestone walls of the city's weaponry glow slightly in the daylight, the warm hue of the stone belying the strength and hardness of its surface.  The windows are thrown open, and the sound of hammer ringing upon anvil drifts across the wey at regular intervals.  A mithglin sign hangs upon the building's doorpost."

Room.exits = {
    south                = 3525,
    north                = 3527,
    go_weaponry          = 10367,
}

Room.indoor = false
Room.safe   = true

return Room
