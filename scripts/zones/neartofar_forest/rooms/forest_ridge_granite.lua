-- Room 10638: Neartofar Forest, Ridge
local Room = {}

Room.id          = 10638
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Ridge"
Room.description = "A vein of lichen-covered granite juts from the earth like an exposed spine at the top of the ridge.  Scraggly spruce trees grow in dense stands at each side of the outcropping, their grey-green needles covering the rocky soil, trapping the rainwater that would otherwise cascade down each slope.  At the side of the trail, a ghostly white owl sits in a tree, its head slowly twisting as it scans the forest for suitable prey."

Room.exits = {
    south                    = 10625,
    north                    = 10639,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
