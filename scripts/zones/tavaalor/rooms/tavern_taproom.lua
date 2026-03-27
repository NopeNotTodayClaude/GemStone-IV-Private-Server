-- Room 10424: Helgreth's Tavern, Taproom
local Room = {}

Room.id          = 10424
Room.zone_id     = 2
Room.title       = "Helgreth's Tavern, Taproom"
Room.description = "Boisterous laughter erupts often from the congregation of imbibing patrons seated at Helgreth's tables.  A scattering of flickering beeswax candles glimmer off the numerous brass fixtures and pristine inverted glassware suspended above the polished bar.  In their starched uniforms, off-duty military officers traverse the tumult of the taproom as they come and go from a plush sanguine velvet curtain marked by a heraldic Vaalorian buckler overhead."

Room.exits = {
    out                  = 3498,
    go_stair             = 10425,
}

Room.indoor = true
Room.safe   = true

return Room
