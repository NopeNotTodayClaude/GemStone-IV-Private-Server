-- Room 10697: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10697
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A tangle of now dry brambles climb up the corner of the outer wall.  The vines seem to have fought each other in their ascent of the wall.  The vines have wormed their way into every available crack, using their new holds to further their journey upwards.  Moonlight throws the corner into shadow, adding a sinister look to the brambles."

Room.exits = {
    east                     = 10698,
    northwest                = 10696,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
