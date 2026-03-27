-- Room 59041: Scenario 4 - Cottage interior
local Room = {}

Room.id          = 59041
Room.zone_id     = 99
Room.title       = "A Humble Cottage"
Room.description = "The interior of the cottage is small and sparsely furnished.  A young girl lies on a narrow cot, her arm wrapped in bloodstained bandages.  Her breathing is shallow but steady.  A small table holds a basin of water and some clean rags."

Room.exits = {
    out = 59040,
}

Room.indoor = true
Room.safe   = true

return Room
