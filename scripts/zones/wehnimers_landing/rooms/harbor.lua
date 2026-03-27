-- Room 126: Harbor Pier
local Room = {}

Room.id          = 126
Room.zone_id     = 1
Room.title       = "Harbor Pier"
Room.description = "Weathered wooden planks creak beneath your feet as you stand on the main pier of Wehnimer's Landing.  Fishing boats and merchant vessels bob gently in their berths.  Nets hang from posts to dry, and coils of heavy rope lie in neat piles.  The open sea stretches to the south, gray-green and endless."

Room.exits = {
    north     = 116,
}

Room.indoor = false
Room.safe   = true

return Room
