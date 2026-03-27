-- Room 10313: Wyvern Keep, Lobby
local Room = {}

Room.id          = 10313
Room.zone_id     = 2
Room.title       = "Wyvern Keep, Lobby"
Room.description = "A gleaming, red marble floor extends at least a hundred feet to the east, its shiny surface reflecting the sunlight that pours through the glass panes high overhead.  White marble columns shot with gold veins support an oak framework two stories up, and large metal baskets filled with trailing ivy and climbing roses hang from the oak mesh.  Immaculate, carved chairs occupy places around the lobby near tables polished to a mirror-like sheen."

Room.exits = {
    out                  = 3487,
    east                 = 10317,
    north                = 10314,
}

Room.indoor = true
Room.safe   = true

return Room
