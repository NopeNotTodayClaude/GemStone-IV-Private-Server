-- Room 10663: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10663
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "A few small pens have been erected against the back of the blockhouse, their split pine rails secured with rope-like vines.  Loose straw covers the hard-packed earth, perhaps to create a comfortable resting place--but there are no signs to indicate what animals inhabited the pens.  A rickety wooden ladder leans against the outer wall, providing access to the northern gallery."

Room.exits = {
    southeast                = 10661,
    up                       = 10664,
    southwest                = 10665,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
