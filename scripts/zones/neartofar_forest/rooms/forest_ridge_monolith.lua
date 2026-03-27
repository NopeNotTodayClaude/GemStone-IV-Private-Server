-- Room 10640: Neartofar Forest, Ridge
local Room = {}

Room.id          = 10640
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Ridge"
Room.description = "An enormous granite monolith thrusts out of the earth, towering over the rest of the ridge's stony spine.  Its commanding height affords a view of the entire forest for anyone foolhardy enough to climb its moss-slick sides.  Someone or something gained the apex, as a large circle of spruce branches rests atop the stone.  Where the monolith meets the ridge top, hundreds of spruce cones have been piled against the base, their partially-burned condition accounting for the sooty smudges on the granite."

Room.exits = {
    south                    = 10639,
    north                    = 10641,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
