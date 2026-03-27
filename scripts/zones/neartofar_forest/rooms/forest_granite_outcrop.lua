-- Room 10624: Neartofar Forest
local Room = {}

Room.id          = 10624
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The broad oak trees that dominate this section of the forest grow so thickly as to obscure the lay of the land.  The trail crosses a granite outcropping, the way marked by innumerable scuff marks, which have erased the burnt orange lichen that covers all but the middle of the stone."

Room.exits = {
    southwest                = 10623,
    northeast                = 10625,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
