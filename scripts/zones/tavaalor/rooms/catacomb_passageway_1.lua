-- Room 5926: Catacombs, Passageway
local Room = {}

Room.id          = 5926
Room.zone_id     = 2
Room.title       = "Catacombs, Passageway"
Room.description = "The ceiling and walls to the east have cracked and crumbled under the weight of the solid ground above.  A makeshift brace lies broken off to the side of the passageway.  An elven corpse lies half buried under a large boulder that fell from the ceiling.  Rotten torches and wooden mallets are scattered among the rocky debris."

Room.exits = {
    west                 = 5925,
    east                 = 5927,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
