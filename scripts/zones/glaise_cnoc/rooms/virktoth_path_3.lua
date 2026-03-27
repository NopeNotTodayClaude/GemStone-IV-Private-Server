-- Room 10732: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10732
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "As the stairway turns a railing begins on the outside edge.  Formed from bones fused together the railing provides a much needed aid in the sharp curve.  Strands of spidersilk attached to the railing float in the breeze, dew drips from them, reflecting brightly in the moonlight."

Room.exits = {
    east                     = 10731,
    southwest                = 10733,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
