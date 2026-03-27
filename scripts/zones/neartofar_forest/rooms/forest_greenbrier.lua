-- Room 10623: Neartofar Forest
local Room = {}

Room.id          = 10623
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "As the trail reaches the base of an incline, thorny greenbrier fills the close spaces between the trees with a thick tangle of underbrush.  A pleasant breeze carries with it a thick, loamy smell and sends dark brown oak leaves swirling over the hard-packed earth of the trail.  The avenue of trees gradually disappears into the densely wooded forest."

Room.exits = {
    southwest                = 10622,
    northeast                = 10624,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
