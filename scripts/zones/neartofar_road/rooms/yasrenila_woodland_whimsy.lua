-- Room 34458: Woodland Whimsy
local Room = {}

Room.id          = 34458
Room.zone_id     = 5
Room.title       = "Woodland Whimsy"
Room.description = "Tangled briars border the space, nearly enclosing it in a thorny embrace as they bend overhead like a prickly, sky-blocking shroud.  Remnants of a long-dried stream, raised shelves of stratified rock frame either side, extending past the threat of the brambles.  Scattered lanterns light the assortment of wooden jewelry arranged upon the brittle, crumbling ledges."

Room.exits = {
    go_briars                = 34456,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
