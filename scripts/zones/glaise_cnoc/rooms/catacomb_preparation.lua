-- Room 10690: Catacomb, Preparation Room
local Room = {}

Room.id          = 10690
Room.zone_id     = 3
Room.title       = "Catacomb, Preparation Room"
Room.description = "A large marble table sits in the center of this room.  Cabinets and shelves line the walls, filled with various instruments, jars and urns.  The air is chill, whether by design or accident, and a pungent odor fills the room."

Room.exits = {
    east                     = 10686,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
