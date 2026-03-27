-- Room 10659: Neartofar Forest
local Room = {}

Room.id          = 10659
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A steep gully leads down from the road, its banks lined with gravel to prevent erosion during the sudden rainstorms that sometimes drench both forest and road.  At the foot of the gully, a trail leads off between some scrub oak trees and honeysuckle vines that have reclaimed some of the land cleared by the road builders."

Room.exits = {
    climb_gully              = 5831,
    east                     = 10658,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
