-- Room 10674: Glaise Cnoc, Mausoleum
local Room = {}

Room.id          = 10674
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Mausoleum"
Room.description = "Barely visible in the dim light, a long granite table supports a sealed limestone sarcophagus.  No ornamentations decorate the room or the sarcophagus.  The air inside the mausoleum is cool and musty."

Room.exits = {
    out                      = 5843,
}

Room.indoor      = true
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
