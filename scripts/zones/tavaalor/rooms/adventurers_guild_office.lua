-- Room 10334: Adventurers' Guild, Office
local Room = {}

Room.id          = 10334
Room.zone_id     = 2
Room.title       = "Adventurers' Guild, Office"
Room.description = "Layers of overlapping, thick wool carpets cover the floor of this spacious room, presenting a bewildering range of styles spanning the primitive geometrics of Tehir to the subtly shaded hues of Loenthra.  At the far end of the room stands an ebony desk inlaid with intricate marquetry, while closer to the stairs leading down, several leather chairs are gathered around a well-tended fire in the stone hearth.  Heavily shuttered windows allow only a few stray beams of light into the comfortable dimness."

Room.exits = {
    down                 = 10331,
}

Room.indoor = true
Room.safe   = true

return Room
