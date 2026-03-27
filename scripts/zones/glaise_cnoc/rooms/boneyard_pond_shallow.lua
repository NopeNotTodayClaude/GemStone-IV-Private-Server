-- Room 10725: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10725
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "Stepping through the shallow pond, small crunching sounds can be heard with each step.  Looking below the black water with its pinpricks of light, small fragile pieces of bone can be seen under the water.  A rolton skull barely breaks the water's surface to the northeast.  The skull shifts slightly with waves in the water."

Room.exits = {
    northeast                = 10724,
    southwest                = 10726,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
