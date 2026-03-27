-- Room 108: Town Square, Southwest
local Room = {}

Room.id          = 108
Room.zone_id     = 1
Room.title       = "Town Square, Southwest"
Room.description = "The southwestern corner of the square is quieter than the rest.  A large old oak tree provides shade over a cluster of wooden benches.  Carved initials and small messages cover the tree's trunk, testaments to countless visitors over the years."

Room.exits = {
    northeast = 100,
    north     = 104,
    east      = 102,
    southwest = 117,
}

Room.indoor = false
Room.safe   = true

return Room
