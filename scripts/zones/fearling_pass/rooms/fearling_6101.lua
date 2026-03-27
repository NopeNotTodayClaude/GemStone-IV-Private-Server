-- Room 6101: Fearling Pass, Cobbled Road
local Room = {}
Room.id          = 6101
Room.zone_id     = 9
Room.title       = "Fearling Pass, Cobbled Road"
Room.description = "The surrounding wold is dotted with plenty of trees, mostly in clusters or small stands nowhere near as thick as the dark forest to the east.  The cobblestone road here is older, its surface uneven where tree roots have begun to buckle the fitted stones.  The road curves northeast toward a rocky trail."
Room.exits = {
    south                    = 3557,
    northeast                = 10270,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
