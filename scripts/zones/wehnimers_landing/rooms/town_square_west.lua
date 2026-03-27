-- Room 104: Town Square, West
local Room = {}

Room.id          = 104
Room.zone_id     = 1
Room.title       = "Town Square, West"
Room.description = "The western edge of the square borders a row of stone buildings, their facades adorned with hanging signs depicting various trades.  A narrow alleyway disappears between two buildings to the west.  A town crier stands on a small wooden platform, occasionally shouting the latest news."

Room.exits = {
    east      = 100,
    north     = 106,
    south     = 108,
    west      = 112,
    go_alley  = 113,
}

Room.indoor = false
Room.safe   = true

return Room
