-- Room 31467: Shadowed Forest, Trail
local Room = {}

Room.id          = 31467
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Sending dark shadows over the forest, the entwined tops of a wide variety of imposing trees obstruct the light attempting to filter through.  Thin slivers of light peek between small gaps in the coverage, descending upon a thick coating of dried leaves below.  Rich, earthy scents float from the still, humid air that barely catches the faint sounds of woodland creatures."

Room.exits = {
    west                     = 31466,
    southeast                = 31468,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
