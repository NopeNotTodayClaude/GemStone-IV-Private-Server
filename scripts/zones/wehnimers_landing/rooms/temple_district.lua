-- Room 114: Temple Courtyard
local Room = {}

Room.id          = 114
Room.zone_id     = 1
Room.title       = "Temple Courtyard"
Room.description = "A peaceful courtyard paved with white marble stretches before a grand temple.  Tall columns support an ornate portico, and the sound of chanting drifts from within.  Well-tended gardens flank the entrance, filled with fragrant herbs and flowering bushes.  An aura of tranquility pervades the area."

Room.exits = {
    southwest = 105,
    go_temple = 125,
}

Room.indoor = false
Room.safe   = true
Room.supernode = true

return Room
