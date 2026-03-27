-- Room 31458: Shadowed Forest, Trail
local Room = {}

Room.id          = 31458
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "The thick cover of maple and oak trees trees block out almost all light, creating a humid and damp environment below.  Piles of dead leaves outline the path alongside colorful clusters of fungi thriving in the moist conditions.  Small tracks indicate the considerable traffic of woodland creatures."

Room.exits = {
    west                     = 31457,
    southeast                = 31459,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
