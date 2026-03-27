-- Room 10703: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10703
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "A sea of grey soil spreads eastward from this point.  Not far ahead, a pair of parallel walls begin to cut through the night.  The bleached material forming the wall is smooth like polished bone.  Watching like tireless sentinels, a pair of humanoid skulls cap the ends of the walls.  Small candles burn inside the skulls, giving the area an orange tint."

Room.exits = {
    east                     = 10704,
    southwest                = 10702,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
