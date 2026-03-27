-- Room 125: Temple Interior
local Room = {}

Room.id          = 125
Room.zone_id     = 1
Room.title       = "Temple of Lorminstra"
Room.description = "The temple interior is vast and hushed, lit by hundreds of flickering candles.  Tall stained glass windows cast pools of colored light across the stone floor.  An altar of polished white marble stands at the far end, and the scent of incense hangs heavy in the air.  A robed cleric tends to the altar with quiet devotion."

Room.exits = {
    out = 114,
}

Room.indoor = true
Room.safe   = true

return Room
