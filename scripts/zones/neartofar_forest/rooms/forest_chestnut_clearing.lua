-- Room 10646: Neartofar Forest
local Room = {}

Room.id          = 10646
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail passes through a large clearing surrounded by tall chestnut trees.  A few crabapple trees have sprouted here and there across the clearing, perfuming the air with their sickly-sweet blooms.  Overhead, some bats careen across the night sky in a frenetic display of energy."

Room.exits = {
    northeast                = 10645,
    southwest                = 10647,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
