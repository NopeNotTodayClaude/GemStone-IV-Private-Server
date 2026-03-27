-- Room 10643: Neartofar Forest, Hillside
local Room = {}

Room.id          = 10643
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Hillside"
Room.description = "The side of the hill has been cleared of trees and underbrush to a distance of two hundred yards from the summit.  A forbidding stockade commands the hillside, its sturdy oak walls and high ramparts securing the hilltop against unwelcome intrusion.  The surrounding grass has been trampled flat, denying cover to those approaching the stockade."

Room.exits = {
    south                    = 10642,
    northeast                = 10644,
    northwest                = 10657,
    go_stockade              = 10660,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
