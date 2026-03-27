-- Room 34449: Neartofar Forest, Path
local Room = {}

Room.id          = 34449
Room.zone_id     = 5
Room.title       = "Neartofar Forest, Path"
Room.description = "Abundant deciduous trees contrast the scarcity of undergrowth, though hints of new life burgeon beneath the copious canopy.  In the early stages of decay, a massive fallen elm serves as a haven to monk's-hood lichen and crawling insects, the center of its toppled form cut out to allow the trail to continue uninterrupted."

Room.exits = {
    southwest                = 34448,
    northwest                = 34450,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
