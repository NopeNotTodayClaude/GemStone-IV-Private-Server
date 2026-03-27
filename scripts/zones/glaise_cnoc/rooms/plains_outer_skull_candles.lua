-- Room 10714: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10714
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Humanoid skulls begin to line the bottom edges of both walls.  Wax from spent candles now runs in frozen rivers down the sides of skulls.  A puddle of stagnant water surrounds one of the skulls, attracting various insects to the area.  Glow-bugs dart around the water, winking their lights slowly."

Room.exits = {
    east                     = 10713,
    west                     = 10715,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
