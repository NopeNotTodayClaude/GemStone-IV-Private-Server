-- Room 31520: Lasimor Circle
local Room = {}

Room.id          = 31520
Room.zone_id     = 5
Room.title       = "Lasimor Circle"
Room.description = "Soft floral fragrances waft through the air as pink and lavender water lilies float on the pond, their large leaves holding up a handful of brightly colored amphibians.  Nestled among the greenery is an ivory stone bench carved in floral filigree.  Slight buzzing noises from the bees harvesting pollen from the irises are the only sounds to break the ambient silence."

Room.exits = {
    northwest                = 31519,
    southwest                = 31522,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
