-- Room 5924: Catacombs, Altar
local Room = {}

Room.id          = 5924
Room.zone_id     = 2
Room.title       = "Catacombs, Altar"
Room.description = "Thick bluish-green mold covers the walls entirely.  Sudden cracks and holes in the ground make walking treacherous.  In each corner of the room, stands considerably sized candelabras with partially burnt blood-red candles perched atop them.  A wooden lectern rests atop a raised, rock platform in the center of the room.  An old tome lies open on the lecturn."

Room.exits = {
    south                = 5923,
    east                 = 5925,
    west                 = 5947,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
