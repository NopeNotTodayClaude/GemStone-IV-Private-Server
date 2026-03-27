-- Room 10328: Areacne's Heirloom Treasures
local Room = {}

Room.id          = 10328
Room.zone_id     = 2
Room.title       = "Areacne's Heirloom Treasures"
Room.description = "Heavy cloth-of-gold curtains frame a pair of windows, glinting in the sunlight filtered through heavy silk sheers.  A lithe elven woman, elegantly attired in a layered black duponi silk gown, moves serenely among the velvet-draped tables dotted about the room, adjusting their displays of glittering jewels and heirloom pieces to best advantage."

Room.exits = {
    west                 = 10327,
    north                = 18089,
}

Room.indoor = true
Room.safe   = true

return Room
