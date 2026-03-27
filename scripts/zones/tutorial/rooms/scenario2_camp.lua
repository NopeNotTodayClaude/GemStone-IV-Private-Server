-- Room 59020: Scenario 2 - The Camp (Inventory/Equipment)
-- Teaches: GET, DROP, WEAR, REMOVE, inventory commands

local Room = {}

Room.id          = 59020
Room.zone_id     = 99
Room.title       = "A Small Camp"
Room.description = "A rough campsite has been set up beside the blue-lit path.  A threadbare bedroll lies next to the remains of a campfire, its embers long cold.  A young warrior sits on a log, head bowed, looking thoroughly dejected.  His empty scabbard hangs at his side."

Room.exits = {
    southeast = 59002,
    north     = 59021,
}

Room.indoor = false
Room.safe   = true

return Room
