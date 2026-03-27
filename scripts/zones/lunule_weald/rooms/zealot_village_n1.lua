-- Room 10612: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10612
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The blackened, skeletal remains of a burnt-out shack stand amongst its ashes and partially burned boards.  The roof and walls were burned and caved in, and only a couple of the corner posts still stand.  An acrid, burnt odor mingles with the musty smell of the fungus overtaking the decay of this small building."

Room.exits = {
    north                    = 10611,
    south                    = 10614,
    southwest                = 10615,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
