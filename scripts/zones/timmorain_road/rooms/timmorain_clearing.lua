-- Room 25637: A Small Clearing
local Room = {}

Room.id          = 25637
Room.zone_id     = 4
Room.title       = "A Small Clearing"
Room.description = "Thick-boled sycamores encircle this grassy clearing, their branches encroaching into the open sky overhead and casting dappled shadows, ever shifting in the breezes.  At the center of the clearing, a circle of stones traces a firepit surrounded by an assortment of logs stood on end, providing rough but functional seating.  A weathered shack crouches between two of the largest trees, its rough wooden shingles nearly matching their mottled trunks."

Room.exits = {
    go_footpath              = 5832,
    go_shack                 = 25636,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
