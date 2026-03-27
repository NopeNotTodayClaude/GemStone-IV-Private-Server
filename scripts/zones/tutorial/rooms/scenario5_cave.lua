-- Room 59051: Scenario 5 - Inside the cave (combat encounter)
local Room = {}

Room.id          = 59051
Room.zone_id     = 99
Room.title       = "Dank Cave"
Room.description = "The cave is dark and damp, the walls glistening with moisture.  The stench is worse in here — a mix of rotting meat and animal musk.  The cave opens into a rough chamber, littered with refuse and gnawed bones.  Something stirs in the shadows at the far end of the chamber."

Room.exits = {
    out   = 59050,
    north = 59052,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
