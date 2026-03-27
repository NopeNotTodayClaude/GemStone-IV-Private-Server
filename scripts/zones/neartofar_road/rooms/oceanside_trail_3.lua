-- Room 31476: Oceanside Forest, Trail
local Room = {}

Room.id          = 31476
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Filtering through the forest, the air is filled with the faint tang of salt and sea.  Climbing hydrangeas hold onto the occasional tree, their white flowers adding a pale beauty and light scent to the dark, thick greenery.  Dried leaves, branches, and tree bark litter the road, causing difficult travel conditions."

Room.exits = {
    west                     = 31475,
    east                     = 31477,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
