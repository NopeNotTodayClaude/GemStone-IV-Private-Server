-- Room 10744: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10744
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The stairway is covered with dirt.  The piles of earth completely cover some of the steps.  One larger pile engulfs five of the steps.  The loose dirt swirls wildly with each gust of wind.  The earth seems to soak up the moon's rays."

Room.exits = {
    east                     = 10743,
    southwest                = 10745,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
