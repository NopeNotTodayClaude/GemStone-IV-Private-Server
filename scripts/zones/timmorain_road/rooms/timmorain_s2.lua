-- Room 5831: Timmorain Road
local Room = {}

Room.id          = 5831
Room.zone_id     = 4
Room.title       = "Timmorain Road"
Room.description = "Massive oaks, maples and sycamores line the cobblestone road, and their branches cross overhead.  The sunlight filters through the leafy canopy to dapple the road with intermittent bright and dark patches.  A brisk wind rustles the trees' upper leaves, but nearer the road the foliage softens the gusts, turning them into a warm, gentle breeze."

Room.exits = {
    southwest                = 5830,
    northeast                = 5832,
    climb_gully              = 10659,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
