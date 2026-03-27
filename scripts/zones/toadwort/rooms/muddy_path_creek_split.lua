-- Room 10504: The Toadwort, Muddy Path
local Room = {}

Room.id          = 10504
Room.zone_id     = 7
Room.title       = "The Toadwort, Muddy Path"
Room.description = "The narrow creek breaks off in three different directions.  This bowl-shaped section is almost completely empty.  A large rock placed at its mouth prevents much of the water from entering.  What little water there was has seeped into the ground and the resulting mixture is very thick mud.  A horde of midge larvae and various other infaunas slither and bump along the surface of the mud."

Room.exits = {
    north                    = 10503,
    southwest                = 10505,
    southeast                = 10507,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
