-- Room 10510: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10510
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "A gap in the trees and shrubs reveals a partially concealed trail, which makes it possible to venture closer to the ancient red mangrove.  From this angle, there is a better view of the twisted and gnarled roots, which still appear to be in search of food.  The grisly remains of at least three corpses entangled in some roots are now clearly visible.  One of the roots is still wrapped, though now loosely, around the throat of one of its victims."

Room.exits = {
    northeast                = 10506,
    southeast                = 10509,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
