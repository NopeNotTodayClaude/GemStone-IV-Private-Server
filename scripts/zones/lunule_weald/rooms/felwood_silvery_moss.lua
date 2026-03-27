-- Room 10560: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10560
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "Long strands of silvery moss hang from the branches of the dark fel trees and the trunks are covered in soft, green lichen.  The forest floor is soft with decay and the canopy overhead is thick with deep green leaves."

Room.exits = {
    southwest                = 10559,
    northeast                = 10561,
    south                    = 10572,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
