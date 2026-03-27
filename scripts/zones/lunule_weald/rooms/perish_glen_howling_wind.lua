-- Room 10582: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10582
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "Dark, dead trees crowd the area at every turn, making it difficult to distinguish one from the other.  The howling wind scatters the dead debris into the air, shredding spider webs and assailing the trunks of the trees."

Room.exits = {
    northeast                = 10581,
    east                     = 10583,
    west                     = 10584,
    southeast                = 10591,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
