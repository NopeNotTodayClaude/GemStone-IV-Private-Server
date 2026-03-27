-- Room 10662: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10662
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "The eastern section of the upper wall serves as a loading bay.  A large section of the outer wall has been cut and attached to rawhide hinges, allowing it to fold down during loading operations.  A long pole sticks out over the wall, with rope and pulleys attached to raise cargo to the height.  Large stones line the outer wall in several rows."

Room.exits = {
    down                     = 10661,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
