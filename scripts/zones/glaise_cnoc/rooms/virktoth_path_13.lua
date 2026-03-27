-- Room 10742: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10742
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "A statue of a drake skeleton clings to the side of the hill, the dragon's neck arching over the stairway.  One of the large ribs has been broken in two.  The creature's impressive head looks down the hill, the rubies that serve as eyes seeming to glow with the slightest bit of moonlight."

Room.exits = {
    west                     = 10741,
    southeast                = 10743,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
