-- Room 10711: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10711
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "The tattered remains of an ancient banner hang from two of the skull crenellations on the outer wall.  The strips of cloth move not at all in the utter stillness of the night.  A jumbled pile of bones to one side may once have been a skeleton, though it's impossible to tell what creature the bones might have belonged to due to the presence of three skulls."

Room.exits = {
    north                    = 10710,
    south                    = 10712,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
