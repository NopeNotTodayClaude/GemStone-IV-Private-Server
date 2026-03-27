-- Room 10687: Catacomb, Pyre
local Room = {}

Room.id          = 10687
Room.zone_id     = 3
Room.title       = "Catacomb, Pyre"
Room.description = "The large table in the center of this room is designed to serve as a funeral pyre.  Used to cremate bodies, the table has been somehow crafted to withstand extreme heat.  Stacks of wood and urns of oil line the back wall.  The ceiling of this room slopes upward at the center forming a flue that sucks air and smoke up and outside."

Room.exits = {
    east                     = 10688,
    south                    = 10686,
    west                     = 10689,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
