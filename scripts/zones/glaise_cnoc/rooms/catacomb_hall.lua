-- Room 10686: Catacomb, Hall
local Room = {}

Room.id          = 10686
Room.zone_id     = 3
Room.title       = "Catacomb, Hall"
Room.description = "This small hall is merely the nexus leading to the adjacent rooms.  Void of all furnishings, the smallest sound is magnified and echoes hollowly through the room.  Dim candlelight from a pair of wall sconces illuminates the hall."

Room.exits = {
    north                    = 10687,
    east                     = 10691,
    south                    = 10685,
    west                     = 10690,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
