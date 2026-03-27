-- Room 10639: Neartofar Forest, Ridge
local Room = {}

Room.id          = 10639
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Ridge"
Room.description = "Summerberry bushes thrive in the cooler air blowing across the top of the ridge.  Those few spruces that successfully compete with the shrubbery have been shaped into flag trees by the unrelenting wind, branches and needles and cones stripped from all but the leeward side of the trunk.  Off to the west and far below, a moonlit river runs through the dark forest like a vein of mithril in the deepest cave."

Room.exits = {
    south                    = 10638,
    north                    = 10640,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
