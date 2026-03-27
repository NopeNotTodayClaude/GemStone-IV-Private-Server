-- Room 10529: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10529
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Standing under the starry sky is a lone stone bier that is splattered with brownish stains.  A shallow ditch contains the remains of several unrecognizable and disarranged corpses.  Covering a good portion of the carcasses is a thick, greenish, bubbling liquid.  A rancid stench rides on the vapors, saturating the night air with utter foulness."

Room.exits = {
    northeast                = 10522,
    southwest                = 10528,
    southeast                = 10530,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
