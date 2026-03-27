-- Room 5914: Catacombs, Tunnels
local Room = {}

Room.id          = 5914
Room.zone_id     = 2
Room.title       = "Catacombs, Tunnels"
Room.description = "Oddly deformed mushrooms dot the rocky surface in this chamber."

Room.exits = {
    west                 = 5913,
    go_door              = 5915,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
