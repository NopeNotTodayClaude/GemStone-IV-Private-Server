-- Room 5879: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5879
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The entrance to a crypt stands where four paths converge, creating a crossroads.  The entrance to the crypt is made of granite blocks and only the granite steps leading down are visible.  The crossroads in the path appear to mark the center of the old cemetery."

Room.exits = {
    north                    = 5887,
    east                     = 5888,
    south                    = 5892,
    west                     = 5878,
    go_steps                 = 10685,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
