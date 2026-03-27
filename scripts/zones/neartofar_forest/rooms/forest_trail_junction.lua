-- Room 10642: Neartofar Forest
local Room = {}

Room.id          = 10642
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "Trampled grass marks the beginning of the trails that wander off into the woods to the north.  Directly to the north, the land rises to form a high hill, the only landmark in what is otherwise thick forest as far as the eye can see.  The river to the south rushes quickly but quietly over a rocky ford."

Room.exits = {
    go_river                 = 10633,
    north                    = 10643,
    northeast                = 10647,
    northwest                = 10648,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
