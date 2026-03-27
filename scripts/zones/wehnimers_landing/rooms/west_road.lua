-- Room 112: West Ring Road
local Room = {}

Room.id          = 112
Room.zone_id     = 1
Room.title       = "West Ring Road"
Room.description = "A packed-dirt road follows the inside of the western town wall.  The palisade rises to the west, its timbers dark with age and weather.  A few scattered homes and workshops occupy the land between the road and the wall.  The sound of the harbor is faint but present."

Room.exits = {
    east      = 104,
    north     = 115,
    south     = 117,
}

Room.indoor = false
Room.safe   = true

return Room
