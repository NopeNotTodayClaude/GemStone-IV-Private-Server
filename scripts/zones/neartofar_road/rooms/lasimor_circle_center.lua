-- Room 31522: Lasimor Circle
local Room = {}

Room.id          = 31522
Room.zone_id     = 5
Room.title       = "Lasimor Circle"
Room.description = "Water lilies encircle a tall lasimor tree that towers over the beautiful garden.  The murky water of the pond ripples around the roots while small fish dart about.  Lush greenery from ferns to colorful grasses surround the area and push up against the polished granite stones of the circle."

Room.exits = {
    northeast                = 31520,
    northwest                = 31521,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
