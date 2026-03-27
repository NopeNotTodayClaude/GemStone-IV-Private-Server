-- Room 120: Guard House
local Room = {}

Room.id          = 120
Room.zone_id     = 1
Room.title       = "Guard House"
Room.description = "The interior of the guard house is spartan but well-maintained.  A long wooden table dominates the center of the room, covered with maps and patrol schedules.  Weapon racks line the walls, holding swords, spears, and crossbows in orderly rows.  A stone fireplace crackles in the corner."

Room.exits = {
    go_square = 101,
}

Room.indoor = true
Room.safe   = true

return Room
