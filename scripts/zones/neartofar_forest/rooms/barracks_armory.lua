-- Room 10668: Neartofar Forest, Barracks
local Room = {}

Room.id          = 10668
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Barracks"
Room.description = "Originally a large, single-room structure, the log blockhouse has been divided up into smaller rooms by interior brick walls.  This chamber once served as an armory, the walls covered with various racks and pegs designed to hold arms, armor, and shields.  The stores have long been depleted, leaving only broken remnants in a large pile at each corner of the room."

Room.exits = {
    out                      = 10660,
    north                    = 10669,
    west                     = 10671,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
