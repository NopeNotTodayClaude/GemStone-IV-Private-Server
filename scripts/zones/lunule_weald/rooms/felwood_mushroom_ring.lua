-- Room 10572: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10572
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "The air is still and quiet, only the canopy stirring slightly in an unseen breeze above the forest.  A circle of flat-capped mushrooms grows around the base of a wide fel tree.  The forest floor is soft with a thick layer of dead leaves and twigs."

Room.exits = {
    west                     = 10559,
    north                    = 10560,
    east                     = 10571,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
