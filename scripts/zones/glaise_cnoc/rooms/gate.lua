-- Room 5834: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5834
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The path is flanked by stately tanik trees and widens as it passes between tall black iron gates that stand open.  A bronze plaque is firmly affixed to a stone column on the left side of the gates."

Room.exits = {
    north                    = 5835,
    south                    = 5833,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
