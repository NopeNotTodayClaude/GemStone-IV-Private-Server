-- Room 10561: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10561
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "Small saplings struggle in the shadows of the tall, dark trees to find the light of life in which to grow.  Small paths between the trees are mushy with the decay of leaves, branches and unseen death.  The lonely sound of an owl hooting in the distance breaks the monotony of silence."

Room.exits = {
    southwest                = 10560,
    northeast                = 10562,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
