-- Room 31464: Shadowed Forest, Trail
local Room = {}

Room.id          = 31464
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Light breaks through the thick, twisted canopy above, sending narrow rays of diffused illumination to the ground below.  Brush has been uprooted and trampled alongside the barely visible road.  In the disturbed soil, tangled dewberry brambles have taken over, choking out any other vegetation."

Room.exits = {
    west                     = 31463,
    east                     = 31465,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
