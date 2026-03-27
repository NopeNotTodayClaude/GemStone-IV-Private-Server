-- Room 59052: Scenario 5 - Deep cave (boss encounter area)
local Room = {}

Room.id          = 59052
Room.zone_id     = 99
Room.title       = "Deep Cave"
Room.description = "The cave narrows before opening into a final chamber.  The ceiling rises high above, lost in darkness.  A faint growling echoes off the stone walls.  The floor is covered in a thick layer of debris and animal remains."

Room.exits = {
    south = 59051,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
