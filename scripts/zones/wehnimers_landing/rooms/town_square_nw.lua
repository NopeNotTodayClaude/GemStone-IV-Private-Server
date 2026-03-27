-- Room 106: Town Square, Northwest
local Room = {}

Room.id          = 106
Room.zone_id     = 1
Room.title       = "Town Square, Northwest"
Room.description = "The northwestern corner of the town square lies in the shadow of a large stone tower, its battlements rising high above the surrounding rooftops.  A heavy iron-banded door marks the tower's entrance.  Guards can be seen patrolling the ramparts above."

Room.exits = {
    southeast = 100,
    south     = 104,
    east      = 101,
    northwest = 115,
    go_tower  = 122,
}

Room.indoor = false
Room.safe   = true

return Room
