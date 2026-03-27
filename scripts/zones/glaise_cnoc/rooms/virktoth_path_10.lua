-- Room 10739: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10739
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "Curiously, a wooden post, now mostly rotten, juts out from the hill just above the steps.  The dirt at the base of the post is packed, indicating that it was intentionally placed like this.  A grey brick rests on top of the post, its purpose unknown.  The post seems to reach towards the stars above."

Room.exits = {
    northeast                = 10740,
    southwest                = 10738,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
