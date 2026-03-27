-- Room 31521: Lasimor Circle
local Room = {}

Room.id          = 31521
Room.zone_id     = 5
Room.title       = "Lasimor Circle"
Room.description = "Fitted against the outer curve of the wall, an ivory stone bench carved in floral filigree provides a resting spot and a perfect view of the fish in the pond.  Flanking the seat, vines of clematis grow upward along the wall, providing a bit of privacy.  The scent of salt and sea hangs in the air."

Room.exits = {
    northeast                = 31519,
    southeast                = 31522,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
