-- Room 5866: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5866
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Following the fence, the path meanders to the northwest.  Gentle slopes and a path clear of debris makes walking here easy.  To the northeast, the path splits off and winds its way up a hillock.  A towering willow tree stands at the fork in the path, its long, slender, drooping branches swaying gracefully at the slightest breeze."

Room.exits = {
    northwest                = 5865,
    southeast                = 5835,
    northeast                = 5867,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
