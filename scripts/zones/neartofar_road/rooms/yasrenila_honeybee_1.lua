-- Room 34452: Yasrenila, Honeybee Circle
local Room = {}

Room.id          = 34452
Room.zone_id     = 5
Room.title       = "Yasrenila, Honeybee Circle"
Room.description = "Sweetly fragrant, domes of honeysuckle part their floral curtains to reveal low doors and glass-paned windows.  Forest gnomes wander the flagstone path that meanders through the dwellings, guided by cheery sunflowers and raised gardens spilling out plentiful blossoms.  Entwined with a pentagonal fence, sweetbriar divides the compound from the forest, a carved beech arbor offering an opening in the center."

Room.exits = {
    go_arbor                 = 34451,
    northwest                = 34453,
    northeast                = 34456,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
