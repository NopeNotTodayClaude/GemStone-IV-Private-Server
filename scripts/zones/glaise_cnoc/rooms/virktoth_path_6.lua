-- Room 10735: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10735
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "A dead bush grew to spread across the stairway when it lived.  Sliced limbs mark where others have cut their way through the obstacle.  Strangely, a pile of complete skeletons rest on the hill directly below the long-dead bush.  The night fog hangs heavily around the skeletons."

Room.exits = {
    northeast                = 10734,
    southeast                = 10736,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
