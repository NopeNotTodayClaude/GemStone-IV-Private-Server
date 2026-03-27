-- Room 10585: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10585
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "The loud creaking and groaning of dead branches swaying and cracking in the wind is broken occasionally by a muffled thud as a limb hits the soft ground.  The incessant howling of the wind continues its eerie song throughout the dead forest."

Room.exits = {
    north                    = 10584,
    south                    = 10586,
    west                     = 10587,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
