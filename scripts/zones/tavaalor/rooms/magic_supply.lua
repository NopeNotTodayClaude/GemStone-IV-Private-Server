-- Room 10364: Elantaran's Magic Supply
local Room = {}

Room.id          = 10364
Room.zone_id     = 2
Room.title       = "Elantaran's Magic Supply"
Room.description = "An eclectic mix of glassware fills a pair of long tables.  Beakers, tubes and dishes make up most of the glassware.  Each table is supported by four legs carved to resemble rampant dragons.  A stunningly carved rolltop desk made from beautiful mahogany rests in one corner.  Quills, scrolls and one overly large bottle of black ink reside on the desktop.  A beautifully crafted scroll case towers over the desk, its many slots for scrolls mostly occupied now by a number of tomes."

Room.exits = {
    out                  = 3529,
    west                 = 10365,
}

Room.indoor = true
Room.safe   = true

return Room
