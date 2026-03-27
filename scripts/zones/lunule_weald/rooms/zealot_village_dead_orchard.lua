-- Room 10598: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10598
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Several fruit trees have been planted in two rows here.  The dead trees are bare and rotting fruit, leaves and branches litter the ground around them.  Their withered trunks have been ravaged with disease and parasites, their thin, skeletal branches reaching out like bony fingers."

Room.exits = {
    northeast                = 10597,
    northwest                = 10599,
    west                     = 10602,
    north                    = 10604,
    southeast                = 10613,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
