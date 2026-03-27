-- Room 119: South Gate
local Room = {}

Room.id          = 119
Room.zone_id     = 1
Room.title       = "South Gate"
Room.description = "The south gate of Wehnimer's Landing stands open, its heavy oak doors reinforced with iron bands.  Two guard towers flank the gate, manned by vigilant sentries.  Beyond the gate, a dirt road leads south into the grasslands and toward the distant Locksmehr River."

Room.exits = {
    northeast = 110,
}

Room.indoor = false
Room.safe   = true

return Room
