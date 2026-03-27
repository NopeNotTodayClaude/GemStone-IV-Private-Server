-- Room 10571: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10571
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "Dead leaves periodically float gently to the forest floor as the breeze in the canopy above shakes them loose from their branches.  Intermittent shafts of light pierce the gloom of this dark forest, the thick moss shining silvery in the sunlight."

Room.exits = {
    east                     = 10570,
    west                     = 10572,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
