-- Room 34457: Honeycomb Hodgepodge
local Room = {}

Room.id          = 34457
Room.zone_id     = 5
Room.title       = "Honeycomb Hodgepodge"
Room.description = "Painted in bold yellow and deep black hues, garlands of carved beads and vellum-winged wood honeybees are strung about the birch frame of the stall.  A honeycomb-stitched canvas canopy shades the well-sanded counter displaying neat rows of beeswax candles and honey jars alongside assorted other wares.  Winking with fireflies, profusions of moonlit blossoms spring up on either side of the stand."

Room.exits = {
    out                      = 34456,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
