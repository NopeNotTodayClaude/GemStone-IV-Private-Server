-- Room 10635: Neartofar Forest
local Room = {}

Room.id          = 10635
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail passes under the shadow of some towering oaks, which litter the ground with their variously shaped leaves.  Juniper bushes form a thick underbrush between the trees, their fragrant berries reminiscent of cheap alehouse gin."

Room.exits = {
    south                    = 10634,
    north                    = 10636,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
