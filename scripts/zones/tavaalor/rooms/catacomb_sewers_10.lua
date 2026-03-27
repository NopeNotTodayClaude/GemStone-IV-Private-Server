-- Room 5947: Catacombs, Sewers
local Room = {}

Room.id          = 5947
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "The low uneven ceiling with jagged protrusions makes walking upright burdensome."

Room.exits = {
    east                 = 5924,
    west                 = 5946,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
