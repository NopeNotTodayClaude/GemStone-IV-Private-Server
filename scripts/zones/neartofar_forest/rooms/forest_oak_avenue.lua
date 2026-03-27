-- Room 10622: Neartofar Forest
local Room = {}

Room.id          = 10622
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "An avenue of tall oak trees marks each side of a path that leads deep into Neartofar Forest.  The tree line runs up and over a slight rise to the northeast, then disappears, creating an impression of vast distance that is contradicted by the experience of covering the ground."

Room.exits = {
    go_trail                 = 10497,
    northeast                = 10623,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
