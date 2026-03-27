-- Room 10362: Vonder's Archery Supply
local Room = {}

Room.id          = 10362
Room.zone_id     = 2
Room.title       = "Vonder's Archery Supply"
Room.description = "A newly polished mahogany counter spans the length of the room, completely dividing the room in half.  Several unfinished bows hang from a rack situated behind the counter, along with several displays holding various types of archery supplies."

Room.exits = {
    out                  = 3533,
    south                = 10363,
}

Room.indoor = true
Room.safe   = true

return Room
