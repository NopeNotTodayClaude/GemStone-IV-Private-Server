-- Room 34462: Freshly Foraged
local Room = {}

Room.id          = 34462
Room.zone_id     = 5
Room.title       = "Freshly Foraged"
Room.description = "Rectangular reed baskets brim with roots, mushrooms, and bundles of greens, their earthy and herbaceous fragrances permeating the air.  Piled with diced vegetables, a chopping board rests on the birch counter set between a potbelly stove and a scattering of elm tables.  Assorted herbs dry overhead, strung from a crossbeam that spans from above the open doorway to over the framed watercolor decorating the opposite wall."

Room.exits = {
    out                      = 34461,
    go_doorway               = 34463,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
