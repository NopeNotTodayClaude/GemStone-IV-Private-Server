-- Room 5835: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5835
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "The well-trod path splits here as it follows the fence to the northeast and northwest.  A worn thanot door appears to enter a hillock to the north.  The hillock is moss-covered, with ivy climbing the flat southern face to which the door has been securely affixed."

Room.exits = {
    south                    = 5834,
    northeast                = 5836,
    northwest                = 5866,
    go_door                  = 10673,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
