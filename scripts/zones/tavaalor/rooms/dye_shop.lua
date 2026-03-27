-- Room 13547: Ta'Vaalor Dye Wares, Main Room
local Room = {}

Room.id          = 13547
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Dye Wares, Main Room"
Room.description = "Smoothly polished oak walls reflect soft light from the high ceiling's chandelier.  A long table stretches across the front wall.  Several barrels sit at the end of the table, opposite of the door.  A series of oak pedestals stands in the center of the room, highlighting several pieces of merchandise."

Room.exits = {
    out                  = 3511,
    west                 = 13706,
    east                 = 13707,
    north                = 13708,
}

Room.indoor = true
Room.safe   = true

return Room
