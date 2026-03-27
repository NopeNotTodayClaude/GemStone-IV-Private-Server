-- Room 10630: Neartofar Forest, Riverside
local Room = {}

Room.id          = 10630
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Riverside"
Room.description = "A break in the line of willow trees affords a clear view of the river.  The water moves slowly across the flat land, carrying a variety of leaves and twigs on its glossy surface.  Several brown trout lie motionless against the rocky bottom, their forms gently outlined by the bright, silvery moonlight."

Room.exits = {
    south                    = 10629,
    north                    = 10631,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
