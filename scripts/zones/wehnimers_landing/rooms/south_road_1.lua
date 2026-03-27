-- Room 110: South Ring Road
local Room = {}

Room.id          = 110
Room.zone_id     = 1
Room.title       = "South Ring Road"
Room.description = "The wide dirt road curves gently as it follows the southern edge of town.  To the south, a tall wooden palisade marks the town wall, and beyond it the wilderness stretches endlessly.  The south gate is visible to the southwest, flanked by two guard towers."

Room.exits = {
    north     = 102,
    southwest = 119,
}

Room.indoor = false
Room.safe   = true

return Room
