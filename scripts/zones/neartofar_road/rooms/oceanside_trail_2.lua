-- Room 31475: Oceanside Forest, Trail
local Room = {}

Room.id          = 31475
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Broad trees with crowns overflowing with leaves shelter the ground below.  Large spaces between branches allow the bright sunlight to stream down, covering the lower plant life in its warm glow.  Dense shrubs edge the pale stone road, while stray bits of lush, darkly colored greenery try to invade."

Room.exits = {
    west                     = 31474,
    east                     = 31476,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
