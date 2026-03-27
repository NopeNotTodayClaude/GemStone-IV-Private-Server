-- Room 10704: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10704
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "The outer wall jumps dramatically in height as it continues to the east, before leveling off at nearly eight feet.  The inner wall droops and soars like a dragon's twisting tail flying through the night.  Large bones, white as a ghost and starkly contrasted against the nighttime sky, cap both walls.  The smooth surface of the outer wall is interrupted by ghastly crenellations formed from humanoid skulls."

Room.exits = {
    east                     = 10705,
    west                     = 10703,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
