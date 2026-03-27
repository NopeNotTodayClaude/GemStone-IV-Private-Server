-- Room 31477: Oceanside Forest, Trail
local Room = {}

Room.id          = 31477
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Shimmering down through breaks in the canopy above, the warm sunlight nourishes the ground below, giving life to a wide variety of wildflowers.  The gentle buzzing of honey bees echoes through the air as they flit about from blossom to blossom.  Weaving through the forest, the stone and shell road disappears around a curve."

Room.exits = {
    west                     = 31476,
    east                     = 31478,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
