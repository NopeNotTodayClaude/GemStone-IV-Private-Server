-- Room 10729: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10729
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "To the west, a grand stairway begins to circle the hill.  Formed from the very earth, the steps are smooth like glass.  The grey earth of the hill crumbles with the slightest touch.  The steps are treacherous in the darkness."

Room.exits = {
    east                     = 10707,
    west                     = 10730,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
