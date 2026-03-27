-- Room 10554: Lunule Weald, Knoll
local Room = {}

Room.id          = 10554
Room.zone_id     = 8
Room.title       = "Lunule Weald, Knoll"
Room.description = "A piercing whistle reverberates through the area, drowning out all other sound.  The ground slopes slightly and the thick grass is slick and treacherous.  A single bleached, jagged bone is set into the ground and tethered to the bone is a small piece of thick blue material, flapping in the light breeze."

Room.exits = {
    northeast                = 10553,
    southeast                = 10555,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
