-- Room 10632: Neartofar Forest, Riverside
local Room = {}

Room.id          = 10632
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Riverside"
Room.description = "A moonlit patch of daffodils rests beneath the star-filled sky, where a bend in the river forces the muddy trail to veer inland.  The gentle breezes that carry through the area bear the flowers' subtle perfume, mingled with the stronger fragrance of pine that wafts down from the ridge.  A pestering cloud of gnats fills the air, their incessant droning buzz signaling their intent to strip the skin from your bones."

Room.exits = {
    south                    = 10631,
    northeast                = 10633,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
