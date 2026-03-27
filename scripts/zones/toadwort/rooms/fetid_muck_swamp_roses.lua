-- Room 10525: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10525
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Dense thickets of swamp roses border the bayou, and a thick covering of pale green duckweed covers the surface of the water.  A lush blanket of decumbent shrubbery covers the standing water as well as the ground in this section of the swamp.  Whorls of pointed oval leaves sprinkled with white flowers and bright red berries along the stems of the shrubs are barely noticeable under the starless night sky."

Room.exits = {
    northeast                = 10524,
    southwest                = 10526,
    northwest                = 10530,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
