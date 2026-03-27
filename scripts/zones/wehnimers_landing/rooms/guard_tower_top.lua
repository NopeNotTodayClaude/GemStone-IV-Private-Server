-- Room 128: Guard Tower, Top
local Room = {}

Room.id          = 128
Room.zone_id     = 1
Room.title       = "Guard Tower, Battlements"
Room.description = "The top of the guard tower offers a commanding view of Wehnimer's Landing and the surrounding countryside.  To the north, the dark line of Upper Trollfang forest stretches to the horizon.  To the south, the harbor glitters in the light.  The town spreads below in a patchwork of rooftops and winding streets."

Room.exits = {
    down = 122,
}

Room.indoor = false
Room.safe   = true

return Room
