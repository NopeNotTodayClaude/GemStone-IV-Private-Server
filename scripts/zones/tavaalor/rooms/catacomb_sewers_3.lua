-- Room 5928: Catacombs, Sewers
local Room = {}

Room.id          = 5928
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "To the west, the cavern narrows considerably as some of the walls have crumbled towards the middle of the passageway.  A clammy breeze stirs some dust into a whirlwind as it passes through the narrow openings in the crumbled stones.  A small river of water winds through the piles of refuse that litter the ground."

Room.exits = {
    west                 = 5927,
    east                 = 5929,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
