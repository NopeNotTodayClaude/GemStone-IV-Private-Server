-- Room 31479: Oceanside Forest, Trail
local Room = {}

Room.id          = 31479
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Meandering through the stands of trees, the pebbled road guides the way.  The magnificent sentinels tower from above with their leaf-covered crowns.  Small creatures skitter about in the dry brush before scampering into hiding."

Room.exits = {
    northwest                = 31478,
    south                    = 31480,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
