-- Room 34448: Neartofar Forest, Path
local Room = {}

Room.id          = 34448
Room.zone_id     = 5
Room.title       = "Neartofar Forest, Path"
Room.description = "Saplings and seedlings sprout from the shadowy forest floor in dapples of moonlight, their pliable stems peppered with silver-cast, newborn foliage.  Carved deep into the ridged faces of towering old growth, the occasional pentagonal marking guides the distinct, debris-free trail as it wends through the darkened woods."

Room.exits = {
    southwest                = 31446,
    northeast                = 34449,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
