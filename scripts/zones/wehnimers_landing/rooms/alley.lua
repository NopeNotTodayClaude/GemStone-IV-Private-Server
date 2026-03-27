-- Room 113: Narrow Alley
local Room = {}

Room.id          = 113
Room.zone_id     = 1
Room.title       = "Narrow Alley"
Room.description = "This narrow alley squeezes between two tall stone buildings, barely wide enough for two people to pass.  The cobblestones are slick with moisture, and the air carries a faintly unpleasant odor.  Shadows pool in the corners despite the hour."

Room.exits = {
    east      = 104,
}

Room.indoor = false
Room.safe   = false
Room.dark   = true

return Room
