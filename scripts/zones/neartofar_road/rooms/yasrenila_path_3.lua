-- Room 34450: Neartofar Forest, Path
local Room = {}

Room.id          = 34450
Room.zone_id     = 5
Room.title       = "Neartofar Forest, Path"
Room.description = "Winding through the woodland, the trail passes jagged stumps jutting out from the verdure-starved earth, evidence of their former lives scattered in piles laden with mushrooms and snails.  While staggered and sparse, the trees that still stand within the arboreal graveyard are ancient giants, finespun webs caught between them."

Room.exits = {
    southeast                = 34449,
    north                    = 34451,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
