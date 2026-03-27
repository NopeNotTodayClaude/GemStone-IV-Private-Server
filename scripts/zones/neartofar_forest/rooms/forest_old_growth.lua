-- Room 10658: Neartofar Forest
local Room = {}

Room.id          = 10658
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail passes through the area reclaimed by the forest and then plunges into the denser old growth.  Red maples, oaks, and chestnut trees grow so closely together that visibility drops to mere feet.  The sound of wind blowing across the leafy crowns, a gentle shush, masks the noise of movement across the carpet of dried leaves."

Room.exits = {
    southeast                = 10652,
    west                     = 10659,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
