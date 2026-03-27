-- Room 59030: Scenario 3 - The Smuggler (Stealth)
-- Teaches: HIDE, UNHIDE, STEAL, SNEAK

local Room = {}

Room.id          = 59030
Room.zone_id     = 99
Room.title       = "A Shadowed Alley"
Room.description = "The green-lit path has led you into a narrow alley between two crumbling stone walls.  Shadows pool thickly in the corners, and the air carries a faint whiff of pipe smoke.  A sharp-eyed town guard leans against one wall, watching the far end of the alley with keen interest."

Room.exits = {
    west  = 59002,
    east  = 59031,
}

Room.indoor = false
Room.safe   = true

return Room
