-- Room 5925: Catacombs, Sewers
local Room = {}

Room.id          = 5925
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "The flow of the murky water is abruptly halted by a huge mass of garbage.  Rats and roaches hunt through the refuse for signs of food.  Crumpled papers sail across the water on the damp breezes of the cavern.  The walls of the cavern sweat from the cold dampness of the stale air."

Room.exits = {
    west                 = 5924,
    east                 = 5926,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
