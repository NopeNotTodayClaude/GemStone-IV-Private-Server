-- Room 5933: Catacombs, Sewers
local Room = {}

Room.id          = 5933
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "Wet, foul smelling compost lines the floor making interesting squishing sounds underfoot."

Room.exits = {
    southeast            = 5932,
    northwest            = 5934,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
