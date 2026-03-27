-- Room 31480: Oceanside Forest, Trail
local Room = {}

Room.id          = 31480
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Propped upon a small tangle of brush, a fallen oak mars the otherwise verdant forest floor.  The broken trunk has suckers of new growth ringing it, while its discarded branches bend, dry and withered.  Blanketing the rotting wood is a layer of dark green tree moss."

Room.exits = {
    north                    = 31479,
    south                    = 31481,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
