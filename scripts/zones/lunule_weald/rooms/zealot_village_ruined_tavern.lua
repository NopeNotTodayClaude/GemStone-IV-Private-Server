-- Room 10601: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10601
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The wooden remains of a small building lay in a pile of broken wood, glass and other debris.  This building appears to have once been a small tavern since the majority of debris is broken mugs, glasses and pottery.  Sharp pieces of glass scattered on the ground among the leaves and broken wood makes it treacherous to walk around here."

Room.exits = {
    northeast                = 10599,
    southeast                = 10602,
    south                    = 10603,
    north                    = 10618,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
