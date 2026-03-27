-- Room 59040: Scenario 4 - The Wounded Child (Healing)
-- Teaches: TEND, FORAGE, GIVE, basic healing

local Room = {}

Room.id          = 59040
Room.zone_id     = 99
Room.title       = "A Quiet Village Road"
Room.description = "The silver-lit path opens onto a quiet village road.  Small cottages with thatched roofs line the lane.  A young girl stands in the doorway of one cottage, tears streaming down her face.  She clutches the hem of her dress with trembling hands."

Room.exits = {
    east       = 59002,
    go_cottage = 59041,
    north      = 59042,
}

Room.indoor = false
Room.safe   = true

return Room
