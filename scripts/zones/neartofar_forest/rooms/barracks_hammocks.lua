-- Room 10670: Neartofar Forest, Barracks
local Room = {}

Room.id          = 10670
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Barracks"
Room.description = "Thick oak boles running from the ceiling into the floor serve as anchor points for dozens of burlap hammocks.  Arranged in tiers four deep, the hammocks do not offer very spacious or comfortable accommodation, especially were all of them filled at once.  The odors of stale sweat and rotting burlap dominate an air scented with a potpourri of unwholesome smells."

Room.exits = {
    east                     = 10669,
    south                    = 10671,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
