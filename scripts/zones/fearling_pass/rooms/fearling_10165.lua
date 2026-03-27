-- Room 10165: Fearling Pass, Ravine
local Room = {}
Room.id          = 10165
Room.zone_id     = 9
Room.title       = "Fearling Pass, Ravine"
Room.description = "Rushing downhill toward a clump of boulders, a thin stream covers what remains of a navigable trail in this slender gully.  The water is ankle-deep at its worst, icy cold and fast-moving.  The ravine walls close in to the northeast, narrowing to a crevasse."
Room.exits = {
    southwest                = 10164,
    northeast                = 10166,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
