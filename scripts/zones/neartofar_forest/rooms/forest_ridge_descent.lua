-- Room 10641: Neartofar Forest, Ridge
local Room = {}

Room.id          = 10641
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Ridge"
Room.description = "The trail follows a serpentine path as the ridge descends to meet the rest of the forest at its northernmost end.  A few stray granite boulders lie scattered across the forest floor, covered with mosses and lichens that help them to blend with the surrounding flora.  Hearty spruces, grown tall in the better soil at the base of the ridge, mingle with the oaks hearty enough to survive the higher elevation."

Room.exits = {
    north                    = 10633,
    south                    = 10640,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
