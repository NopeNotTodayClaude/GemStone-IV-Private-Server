-- Room 10614: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10614
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The forest has begun to encroach upon this abandoned village.  The thick undergrowth threatens to overtake any buildings or artifacts that still inhabit this place.  Several flexible, limber sprouts are maturing into saplings.  They contain the promise of the living forest reclaiming the land."

Room.exits = {
    north                    = 10612,
    northwest                = 10613,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
