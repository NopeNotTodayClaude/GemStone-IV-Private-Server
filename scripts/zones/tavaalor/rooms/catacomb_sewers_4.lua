-- Room 5929: Catacombs, Sewers
local Room = {}

Room.id          = 5929
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "Faint scratching emanates from behind the walls as rats forage for a snack."

Room.exits = {
    west                 = 5928,
    east                 = 5930,
    north                = 5931,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
