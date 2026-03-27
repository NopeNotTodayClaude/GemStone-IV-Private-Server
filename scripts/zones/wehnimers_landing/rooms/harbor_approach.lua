-- Room 116: Harbor Approach
local Room = {}

Room.id          = 116
Room.zone_id     = 1
Room.title       = "Harbor Approach"
Room.description = "The street slopes gently downward toward the harbor.  The smell of salt water and fish grows stronger with each step.  Wooden pilings and the tops of ship masts are visible ahead, and the cries of seagulls fill the air.  Dock workers haul crates along the road."

Room.exits = {
    northwest = 107,
    south     = 126,
}

Room.indoor = false
Room.safe   = true

return Room
