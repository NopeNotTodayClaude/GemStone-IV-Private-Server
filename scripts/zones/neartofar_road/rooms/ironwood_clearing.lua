-- Room 31465: Ironwood Tree, Clearing
local Room = {}

Room.id          = 31465
Room.zone_id     = 5
Room.title       = "Ironwood Tree, Clearing"
Room.description = "Standing sentinel over the bordering dark forest is a lone ironwood tree, its magnificent crown filled with copper red leaves.  Tangled honeyberry bushes surround the clearing, creating a natural fence around the towering form.  A ring of cobblestones is partially visible under the dirt of the road."

Room.exits = {
    west                     = 31464,
    east                     = 31466,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
