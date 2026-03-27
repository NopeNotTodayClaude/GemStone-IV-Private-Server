-- Room 10332: Adventurers' Guild, Hiring Hall
local Room = {}

Room.id          = 10332
Room.zone_id     = 2
Room.title       = "Adventurers' Guild, Hiring Hall"
Room.description = "This long gathering hall is lined with rough wooden benches and a few posting boards with odd scraps of parchment tacked on them.  A few anxious-looking young men hover about the edges of the room, their nervous pacing a sharp contrast to the resigned attitude of some older folks resting on the benches.  At the far end of the hall, a sturdy maoral table serves as a desk, its contents meticulously arranged."

Room.exits = {
    west                 = 10331,
}

Room.indoor = true
Room.safe   = true

return Room
