-- Room 59000: Tutorial - Arrival
-- First room a new character sees

local Room = {}

Room.id          = 59000
Room.zone_id     = 99
Room.title       = "A Misty Clearing"
Room.description = "You find yourself standing in a small clearing surrounded by swirling silver mist.  The air tingles with magical energy, and the ground beneath your feet feels strangely insubstantial, as though this place exists between the folds of the world itself.  A faint shimmering light bobs in the air before you."

Room.exits = {
    north = 59001,
}

Room.indoor = false
Room.safe   = true

return Room
