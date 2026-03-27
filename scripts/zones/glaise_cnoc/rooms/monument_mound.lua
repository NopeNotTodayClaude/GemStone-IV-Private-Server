-- Room 5876: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5876
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Thick green grass blankets the entire mound.  A tall monument stands six feet high and equally as wide.  A simple wall of granite, the monument is otherwise unadorned except for the names engraved upon it.  The mound is free of flowers and trees.  Only the monument is here, amid a field of grass."

Room.exits = {
    north                    = 5880,
    south                    = 5875,
    west                     = 5877,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
