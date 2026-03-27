-- Room 10371: Hall of the Arkati, Hallway
local Room = {}

Room.id          = 10371
Room.zone_id     = 2
Room.title       = "Hall of the Arkati, Hallway"
Room.description = "A pale green and gold Loenthran runner carpets the narrow hallway from end to end.  Glaesine sconces line the wall at regular intervals, their candles snuffed for the day.  A glaes-paned door leads out into a small courtyard, barely visible through the cloudy diamond-shaped panes."

Room.exits = {
    north                = 10369,
}

Room.indoor = true
Room.safe   = true

return Room
