-- Room 31519: Lasimor Clearing
local Room = {}

Room.id          = 31519
Room.zone_id     = 5
Room.title       = "Lasimor Clearing"
Room.description = "Polished rose granite encloses a perfect circle centered on a still pond lined with riverstones.  Vibrant fish flash in its depths, the dark water barely revealing their antics as they dart back and forth under the colorful water lilies that drift across the surface.  A small gravel path edges the basin, and a cluster of violet irises reveal their soft blooms against the pink enclosure.  Tiny iridescent insects flit about the garden, their translucent wings glittering in the moonlight."

Room.exits = {
    out                      = 31483,
    southeast                = 31520,
    southwest                = 31521,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
