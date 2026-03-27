-- Room 10645: Neartofar Forest
local Room = {}

Room.id          = 10645
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A low ground cover of greenbrier soon becomes a dense thicket that rises above the head of even the tallest of giantkin.  It would be hard to call the path through the briers a trail, as the way only becomes apparent by pushing through the thick brush.  Overhead, some oaks rise out of the thicket, providing some sense of distance and perspective in what would otherwise be a hopeless maze."

Room.exits = {
    west                     = 10644,
    southwest                = 10646,
    northwest                = 10655,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
