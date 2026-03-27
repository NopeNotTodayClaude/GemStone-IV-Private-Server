-- Room 5833: Timmorain Road
local Room = {}

Room.id          = 5833
Room.zone_id     = 4
Room.title       = "Timmorain Road"
Room.description = "A bridge to the northeast has collapsed into a swift stream, and though the cobblestone road obviously continues into the forest on the other side, there is no way to cross the surging waters.  The collapse appears to be rather recent, judging from the condition of the broken timbers, and there is no evidence of repair efforts.  A tree-lined path leads into the forest, perhaps providing a means of circumventing the ruined bridge."

Room.exits = {
    southwest                = 5832,
    go_path                  = 5834,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
