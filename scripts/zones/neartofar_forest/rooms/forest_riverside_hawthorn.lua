-- Room 10631: Neartofar Forest, Riverside
local Room = {}

Room.id          = 10631
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Riverside"
Room.description = "To the east, a thicket of hawthorn parallels the river, its daunting thorns forcing travellers nearer the riverbank.  A deep depression has been carved into the mud, as if someone tried to divert its course.  Apparently, the thick tangle of willow roots that shores up the bank prevented the diggers from achieving their goal."

Room.exits = {
    south                    = 10630,
    north                    = 10632,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
