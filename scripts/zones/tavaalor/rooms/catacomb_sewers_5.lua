-- Room 5932: Catacombs, Sewers
local Room = {}

Room.id          = 5932
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "A thin trickle of rank water flows down from the ceiling, rudely destroying the homes of several spiders."

Room.exits = {
    southeast            = 5931,
    northwest            = 5933,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
