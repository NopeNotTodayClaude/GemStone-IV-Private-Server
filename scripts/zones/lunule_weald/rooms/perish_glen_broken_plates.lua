-- Room 10590: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10590
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "Several broken plates, cups and other eating utensils are scattered among the dead leaves around the trees.  A burlap sack lies rotting in the midst of the kitchenware, as if someone had dumped a sack full of goods in the forest.  Small worms and other insects crawl in and around the debris, making their homes in it."

Room.exits = {
    northwest                = 10589,
    southwest                = 10594,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
