-- Room 124: Adventurer's Guild
local Room = {}

Room.id          = 124
Room.zone_id     = 1
Room.title       = "Adventurer's Guild"
Room.description = "The Adventurer's Guild hall is a large, well-lit room with trophy heads mounted on the walls and a massive map of the region pinned behind the main desk.  A grizzled Taskmaster sits behind the desk, ready to assign bounties to willing adventurers.  A notice board on the wall is covered with job postings and wanted notices."

Room.exits = {
    out = 111,
}

Room.indoor = true
Room.safe   = true

return Room
