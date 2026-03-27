-- Room 10528: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10528
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Ingrown and disfigured trees line up on both sides of a small gully that is filled with water the consistency of tar.  One tree stands out from the rest, because of the way its arm-like branches seem to be straining in an effort to cover its tormented face.  Deep slash marks are visible in the mud as they crisscross through each other.  Some of the tracks make a beeline straight toward the gully, while others head off into the safety of the trees."

Room.exits = {
    southeast                = 10527,
    northeast                = 10529,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
