-- Room 18041: Wizard Guild, Gardens
local Room = {}

Room.id          = 18041
Room.zone_id     = 2
Room.title       = "Wizard Guild, Gardens"
Room.description = "This pocket garden is bounded by the granite wall of the Guardian Keep and the three towers of the Wizard Guild.  Fragrant wisterias climb the limestone blocks of the large, squat tower to the west, while the top of the slender northeast tower is nearly blocked from view by the thick-leafed magnolia overarching this courtyard.  The third tower rises between the two, neither as low as the one nor as slender as the other."

Room.exits = {
    out                  = 3495,
    east                 = 18042,
}

Room.indoor = true
Room.safe   = true

return Room
