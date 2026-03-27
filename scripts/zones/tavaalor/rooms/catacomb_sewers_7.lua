-- Room 5936: Catacombs, Sewers
local Room = {}

Room.id          = 5936
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "Interestingly, the walls have been crafted with stacked bones and skulls in artsy, symmetric patterns."

Room.exits = {
    southeast            = 5935,
    southwest            = 5937,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
