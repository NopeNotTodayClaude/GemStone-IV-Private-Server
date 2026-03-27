-- Room 31450: Neartofar Road, Dam
local Room = {}

Room.id          = 31450
Room.zone_id     = 5
Room.title       = "Neartofar Road, Dam"
Room.description = "Serving as a path across the stream, a wide earthen dam is partially lined with old cobblestones.  Fragrant, twisted olive trees line the meadow on this side of the water, their branches laden with ripening fruit.  Scattered stones show through the dirt and weeds that cover the road."

Room.exits = {
    go_dam                   = 31449,
    southeast                = 31451,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
