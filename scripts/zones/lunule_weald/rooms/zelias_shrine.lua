-- Room 10596: Lunule Weald, Zelia's Shrine
local Room = {}

Room.id          = 10596
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zelia's Shrine"
Room.description = "Worms and insects ooze out of the dirt walls and creep along the floor in this small, squat chamber.  In the center of the chamber is a circle of black rocks, the top of each rock is painted with a silver crescent moon.  Inside the circle of rocks sits a stone sculpture of a woman with wild hair driving a chariot pulled by four stallions.  Moonlight streams in from the opening in the short ceiling, striking the sculpture and casting the shadow of a wild-haired woman on the dirt walls."

Room.exits = {
    go_opening               = 10594,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
