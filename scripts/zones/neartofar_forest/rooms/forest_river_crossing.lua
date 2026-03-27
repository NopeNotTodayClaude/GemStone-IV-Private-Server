-- Room 10633: Neartofar Forest
local Room = {}

Room.id          = 10633
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "Three trails emerge from the forest to the south and converge at the grassy bank of a river.  Frequent passage of travellers' feet has flattened the grass right up to the sandy riverbank, and similar marks on the other side indicate that the river can be crossed by pedestrian travel."

Room.exits = {
    southwest                = 10632,
    southeast                = 10637,
    south                    = 10641,
    go_river                 = 10642,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
