-- Room 34456: Yasrenila, Honeybee Circle
local Room = {}

Room.id          = 34456
Room.zone_id     = 5
Room.title       = "Yasrenila, Honeybee Circle"
Room.description = "Their denizens quiet and unseen in the night, numerous hives stand scattered beneath the umbrageous treetops, slivers of moonlight dappling the cedar frames.  Joined by pale sea glass blooms unfurling from bronze stems, ferns and vibrant wildflowers thrive within maple-slatted flower beds.  The dense forest edging the clearing is broken by a faint trail that disappears into the treeline beside a canopied birch stall."

Room.exits = {
    southwest                = 34452,
    west                     = 34453,
    go_stall                 = 34457,
    go_trail                 = 34458,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
