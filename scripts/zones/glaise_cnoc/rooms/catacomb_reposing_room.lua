-- Room 10693: Catacomb, Reposing Room
local Room = {}

Room.id          = 10693
Room.zone_id     = 3
Room.title       = "Catacomb, Reposing Room"
Room.description = "A silk veil hangs from a hook on the ceiling and drapes around a low granite table in the center of the room.  Four rows of benches surround the table, providing mourners with seating for their vigils.  Wall sconces light the room, their flickering candles providing an eerie glow."

Room.exits = {
    west                     = 10685,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
