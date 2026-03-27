-- Room 10660: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10660
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "Within the stockade's high log walls, bare soil has been trampled into firm pavement by thousands of booted feet.  In the center of the square courtyard stands a squat wooden blockhouse, apparently constructed with neither windows nor doors.  A steep, shallow stairway cut into the logs runs parallel to the wall, leading to a rampart above."

Room.exits = {
    out                      = 10643,
    northeast                = 10661,
    northwest                = 10665,
    up                       = 10667,
    go_barracks              = 10668,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
