-- Room 10501: The Toadwort, Muddy Path
local Room = {}

Room.id          = 10501
Room.zone_id     = 7
Room.title       = "The Toadwort, Muddy Path"
Room.description = "The aromatic scents of various flora fill the air.  Uncountable white avens with their tri-part serrated leaves are almost hidden beneath the towering spotted jewelweed.  Though not quite as beautiful as the spotted jewelweed or as tall as the white avens, slender mountain mints dominate the air with their slender leaves and small white flowers clustering atop a square stem."

Room.exits = {
    up                       = 10500,
    northwest                = 10502,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
