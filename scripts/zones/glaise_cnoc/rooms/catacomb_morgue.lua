-- Room 10691: Catacomb, Morgue
local Room = {}

Room.id          = 10691
Room.zone_id     = 3
Room.title       = "Catacomb, Morgue"
Room.description = "Several granite tables are arranged about this room.  Void of ornamentation, the tables are serviceable rather than decorative.  The only other furniture is a wooden rack of neatly folded sheets.  Candles flicker in wall sconces, casting an eerie glow on the room."

Room.exits = {
    west                     = 10686,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
