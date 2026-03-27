-- Room 10661: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10661
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "Two lines have been scratched deep into the ground at either edge of the courtyard, which is littered with various contraptions that suggest its use as an exercise yard.  A small, brick chimney rises from the northeast corner of the barracks, thick oily smoke rising into the bright blue sky.  A cargo net draped against the outer wall provides a means of climbing to the platform overhead."

Room.exits = {
    southwest                = 10660,
    up                       = 10662,
    northwest                = 10663,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
