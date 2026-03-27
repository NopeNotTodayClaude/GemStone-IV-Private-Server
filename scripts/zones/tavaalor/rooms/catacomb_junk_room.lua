-- Room 5946: Catacombs, Junk Room
local Room = {}

Room.id          = 5946
Room.zone_id     = 2
Room.title       = "Catacombs, Junk Room"
Room.description = "Shredded bits and pieces of clothing from previous adventurers traipsing around down here are stuck to the rough edges of the walls in this circular in shape chamber."

Room.exits = {
    west                 = 5945,
    east                 = 5947,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
