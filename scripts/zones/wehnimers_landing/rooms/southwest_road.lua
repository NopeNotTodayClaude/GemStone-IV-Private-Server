-- Room 117: Southwest Ring Road
local Room = {}

Room.id          = 117
Room.zone_id     = 1
Room.title       = "Southwest Ring Road"
Room.description = "The road curves along the southwest portion of town.  A weathered wooden building with a creaking sign reading 'Wayfarer's Inn' stands to the south.  The warm glow of firelight spills from its windows, and the muffled sound of laughter and clinking mugs drifts out."

Room.exits = {
    northeast = 108,
    north     = 112,
    go_inn    = 127,
}

Room.indoor = false
Room.safe   = true

return Room
