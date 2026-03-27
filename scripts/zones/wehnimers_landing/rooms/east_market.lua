-- Room 111: East Market Street
local Room = {}

Room.id          = 111
Room.zone_id     = 1
Room.title       = "East Market Street"
Room.description = "Market Street bustles with activity.  Rows of wooden stalls line both sides of the thoroughfare, their owners loudly hawking everything from fresh fish to enchanted trinkets.  A large painted sign above a stone building to the north reads 'Adventurer's Guild' in bold letters."

Room.exits = {
    west      = 103,
    east      = 123,
    go_guild  = 124,
}

Room.indoor = false
Room.safe   = true

return Room
