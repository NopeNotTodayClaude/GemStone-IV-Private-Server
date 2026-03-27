-- Room 3746: Hall of Justice, Clerk's Office
local Room = {}

Room.id          = 3746
Room.zone_id     = 2
Room.title       = "Hall of Justice, Clerk's Office"
Room.description = "A heavily carved modwir desk occupies the center of the office.  One wall is lined floor to ceiling with built-in wooden shelves, each one burdened with orderly stacks of files and thick sheaves of parchment."

Room.exits = {
    south                = 10382,
}

Room.indoor = true
Room.safe   = true

return Room
