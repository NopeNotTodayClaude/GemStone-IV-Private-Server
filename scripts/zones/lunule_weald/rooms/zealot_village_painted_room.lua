-- Room 10609: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10609
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "This room is totally empty, even the wooden floor appears to have been swept clean.  Though the room is devoid of furniture and other objects, every space on the walls, floor and ceiling has been painted with odd pictures, symbols and letters.  The chaos of the colors covering every surface of the room creates a dizzying effect."

Room.exits = {
    west                     = 10608,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
