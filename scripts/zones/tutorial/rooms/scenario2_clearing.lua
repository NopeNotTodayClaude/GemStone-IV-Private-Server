-- Room 59021: Scenario 2 - Clearing with sword
local Room = {}

Room.id          = 59021
Room.zone_id     = 99
Room.title       = "A Grassy Clearing"
Room.description = "Tall grass sways in a clearing beyond the camp.  Something metallic glints in the grass near the base of a gnarled oak tree."

Room.exits = {
    south = 59020,
}

Room.indoor = false
Room.safe   = true

return Room
