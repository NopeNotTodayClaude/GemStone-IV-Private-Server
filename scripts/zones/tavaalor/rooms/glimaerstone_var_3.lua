-- Room 3532: Ta'Vaalor, Glimaerstone Var
local Room = {}

Room.id          = 3532
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Glimaerstone Var"
Room.description = "A pale white marble arch breaks the rigid greenery of a thick hedgerow.  The lovely arch is an open invitation to wander the cobbled path leading deeper into its interior.  An engraved mithril sign hangs from one side of the arch."

Room.exits = {
    west                 = 3531,
    south                = 3533,
    go_springs           = 10343,
}

Room.indoor = false
Room.safe   = true

return Room
