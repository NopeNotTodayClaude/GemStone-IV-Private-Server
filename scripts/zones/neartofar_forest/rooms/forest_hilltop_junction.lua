-- Room 10625: Neartofar Forest
local Room = {}

Room.id          = 10625
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail breaks from the deep cover of oak trees just as it reaches the top of a small but high hill.  From that vantage, one can see numerous trails snaking off into the distance.  One trail descends into the river bottom to the northwest.  A second path, to the north, climbs a rocky ridge.  The third traces to the northeast before plunging into a dense forest of towering elms.  The others fork to east and west before disappearing beneath the oaks halfway down the hill to the south."

Room.exits = {
    southwest                = 10624,
    southeast                = 10626,
    northwest                = 10629,
    northeast                = 10634,
    north                    = 10638,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
