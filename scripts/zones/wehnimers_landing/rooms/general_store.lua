-- Room 121: General Store
local Room = {}

Room.id          = 121
Room.zone_id     = 1
Room.title       = "Bregandian's General Store"
Room.description = "Shelves crammed with goods of every description line the walls of this cluttered shop.  Ropes, lanterns, backpacks, and rations compete for space with more exotic items.  A stout merchant stands behind a worn wooden counter, eyeing customers with a practiced mix of friendliness and suspicion."

Room.exits = {
    out = 103,
}

Room.indoor = true
Room.safe   = true

return Room
