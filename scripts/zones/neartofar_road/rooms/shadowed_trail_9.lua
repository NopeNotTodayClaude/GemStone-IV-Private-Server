-- Room 31466: Shadowed Forest, Trail
local Room = {}

Room.id          = 31466
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Dense stands of hawthorn trees straddle the ditches along the side of the road, threatening to scratch with their sharp thorns.  Very little light filters through the leafy branches above, which creates dark shadows about the area.  The buzzing of various insects fills the air as they flit around, enjoying the warm, humid air."

Room.exits = {
    west                     = 31465,
    east                     = 31467,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
