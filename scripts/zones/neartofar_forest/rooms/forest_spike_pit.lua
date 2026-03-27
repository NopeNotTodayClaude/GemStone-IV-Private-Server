-- Room 10655: Neartofar Forest
local Room = {}

Room.id          = 10655
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A large pit has been dug in the middle of the trail, with no attempt made to hide its presence.  Sharp wooden spikes rise from the floor of the pit, designed to incapacitate or kill anything that should fall in.  A large number of boar tracks lead up to the north edge of the pit, but far fewer lead away from the south."

Room.exits = {
    southeast                = 10645,
    northwest                = 10654,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
