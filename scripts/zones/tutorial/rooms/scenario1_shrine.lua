-- Room 59010: Scenario 1 - The Shrine (Communication)
-- Teaches: SAY, ASK, SEARCH

local Room = {}

Room.id          = 59010
Room.zone_id     = 99
Room.title       = "A Weathered Shrine"
Room.description = "A small stone shrine sits at the end of a golden-lit path.  Moss and ivy crawl over its surface, but the carved face of a woman gazing serenely skyward remains clear.  Wilted offerings lie at the base of the shrine.  A hooded figure kneels nearby, muttering quietly."

Room.exits = {
    southwest = 59002,
}

Room.indoor = false
Room.safe   = true

return Room
